#!/usr/bin/env python3
"""PostToolUse hook. Flags that THIS TURN changed something.

A form of the CONDUCTOR, not of any single gate: it is what makes the completion
table fire without being remembered.

WHY BASH IS INCLUDED. On 2026-08-31 a full day of estate work ran through Bash
and ssh, not Write/Edit. A flag keyed only on file-edit tools would have scored
that day as conversational and asked for nothing.

Read-only shells must stay quiet, or the reminder becomes noise and gets ignored
— which is the failure it exists to prevent.
"""
import json, os, re, sys
# __file__ IS NOT DEFINED UNDER exec(). hook_prior_pre loads this module by
# exec-ing its source, so an __file__-based path here broke the predicate
# import outright (2026-09-20) and dropped the PreToolUse form into its
# fail-open branch, warning on plain reads. Caught by the hook itself.
try:
    _HOOKDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HOOKDIR = os.path.expanduser("~/.claude/hooks")
sys.path.insert(0, _HOOKDIR)
try:
    import _flags
except Exception:                     # D2: six hooks share this file. A missing or
    class _flags:                     # half-saved copy must not rc=1 every hook, and
        @staticmethod                 # must never crash ABOVE a once-per-turn guard.
        def payload():
            return {}
        @staticmethod
        def sid(_d):
            return "nosession"
        @staticmethod
        def path(name, session):
            return os.path.join(os.environ.get("TMPDIR", "/tmp"),
                                "coywolf-%s.%s.flag" % (name, session))

# Flag paths are resolved PER SESSION in mark(), from the payload. A fixed
# path under a per-USER TMPDIR let a concurrent session consume them
# (refuted 2026-09-20): the table and the prior were lost on the turn that
# actually committed, and handed to a session that had changed nothing.
# The verb may sit INSIDE a quoted remote command: `ssh den "rm -f /tmp/x"`.
# Anchoring to a command boundary missed that, which is the dominant shape of
# this estate's work. So the boundary includes quotes and plain whitespace, and
# the check FAILS TOWARD FLAGGING: a spurious reminder costs one line, a missed
# one costs the whole table.
# 2026-09-01, operator: "fix the hook so it stops firing every turn."
#
# ROOT CAUSE. The old pattern matched command TEXT, so a mutating verb appearing
# as DATA flagged a build: `grep "rm " file`, a test payload containing
# `git commit`, a heredoc body mentioning a path. And the bare-redirect rule
# `>>?\s*[^|&\s]` matched every heredoc and every `> file`, which is most
# diagnostic pipelines. The result was a reminder on nearly every turn, which is
# how a guard gets trained into noise — the failure it exists to prevent.
#
# THE DISCRIMINATOR THAT SURVIVED. Write/Edit is a reliable build signal; Bash is
# not. So Bash now flags only on verbs that are UNAMBIGUOUS and ANCHORED at the
# start of a command or right after a separator (; && || | newline). A verb
# inside quotes is data, not an action, and no longer counts.
#
# Deliberately dropped: the bare-redirect rule. Writing a file through `>` is
# real, but it fired on every heredoc and diagnostic buffer, and Write/Edit
# already covers authored files.
# OPERATOR RULING 2026-09-02: "Tables are only for when we're touching a repo or
# pushing a build. All this additional text is making it very difficult to do my work."
#
# So the trigger is now REPO/BUILD ONLY. Editing a file is not touching a repo until
# it is committed. Removed: rm, mv, chmod, chown, ln, dd, scp, rsync, and the whole
# Write/Edit branch. Kept: version control, service management, package installs.
#
# The prior wording over-fired for weeks and trained the reminder into noise, which is
# the precise failure it exists to prevent. A guard nobody can work alongside is a
# guard that gets switched off.
MUT = re.compile(
    r"(?:^|[;&|\n])\s*"
    # 2026-09-20: a wrapper chain may sit between the boundary and the verb.
    # env assignments, then any stack of sudo/nohup/time/command/exec, then an
    # optional absolute path. Each token is BOUNDED and specific, so this cannot
    # slide the anchor over arbitrary text the way an unanchored verb would.
    r"(?:env\s+)?(?:\w+=(?:'[^']*'|\"[^\"]*\"|[^\s;&|]*)\s+)*"
    r"(?:(?:sudo|nohup|command|exec)(?:\s+-\w+(?:\s+[^\s-]\S*)?)*\s+|time\s+)*"
    r"(?:/\S*/)?"
    r"(?:git\s+(?:-C\s+\S+\s+)?(?:commit|push|add|checkout|reset|merge|rebase|tag|revert)"
    r"|gh\s+(?:pr|release)"
    r"|launchctl\s+(?:load|unload|bootstrap|bootout|kickstart)"
    r"|(?:python3?\s+-m\s+)?pip3?\s+install|npm\s+(?:ci|install|publish|run\s+build)"
    r"|yarn\s+(?:install|add)|pnpm\s+(?:install|add)|brew\s+install"
    r"|make\b|cargo\s+(?:build|publish)|docker\s+(?:build|push)"
    r"|docker\s+compose\s+(?:up|build)"
    r"|wrangler\s+(?:deploy|publish)|terraform\s+apply)"
    r"\b"
)

# NOTES ARE NOT BUILDS. Operator ruling 2026-09-01: appending to canon or memory
# is the behaviour the conductor WANTS, and charging it a 19-gate table taxes the
# right action. A notes path only escapes when the command is PURELY notes work —
# a git or launchctl call in the same command is still a build.
NOTES = re.compile(
    r"coo/taxes/CONTEXT\.md|/memory/|MEMORY\.md|\.claude/projects/.*\.md", re.I)
STILL_A_BUILD = re.compile(r"\bgit\s|launchctl", re.I)

# WRITES THAT TRAVEL INSIDE A QUOTED REMOTE COMMAND — added 2026-09-19.
#
# THE MISS, MEASURED. MUT above anchors every verb to a command boundary, which is
# correct for local shell but blind to this estate's dominant shape:
#     ssh host 'SOME_ENV=value python3 writer_script.py ARG'
# There is no boundary before the verb, and `ssh` itself is not a mutation. On
# 2026-09-19 a single session made 60+ remote writes across a spreadsheet, a
# document store and two data registers — and this hook scored every one of those
# turns as conversation, so no completion table was ever owed. The operator had to
# ask for the gates twice.
#
# WHY THESE TOKENS AND NOT `ssh`/`scp`. Half this estate's remote calls are READS
# (dump_canon.py, values().get, file listings). Flagging the transport would reinstate
# exactly the over-firing that got MUT narrowed on 2026-09-02, and a guard trained into
# noise is the failure this hook exists to prevent. The tokens below are API write
# calls and named writer scripts: they cannot appear in a read, and they do not occur
# in prose. Deliberately UNANCHORED, because that is the whole point.
# 2026-09-20 REFUTED: the script-name tokens matched anywhere, so READING a file
# named after a writer counted as a build -- `cat .../upload_to_drive.py`,
# `ls -la .../patch_registers.py`, `grep -rn mind_commit ~/repos/` and
# `git log -- upload_to_drive.py` all returned True. They must be INVOKED.
REMOTE_WRITE = re.compile(
    r"\bbatchUpdate\b|files\(\)\.(?:update|create|delete)|values\(\)\.update|"
    r"permissions\(\)\.(?:create|delete)|"
    r"(?:^|[;&|\n]|\bpython3?\s+[^\s;&|]{0,60}?[/]|\bpython3?\s+)"
    r"(?:patch_registers|upload_to_drive|restructure_drive)\.py|"
    r"\bmind_commit\s*\(")


# QUOTED REMOTE MUTATIONS — added 2026-09-20 on operator instruction: "widen MUT
# for quoted remote mutations."
#
# THE MISS, MEASURED THAT DAY. Seven real work shapes from one evening were run
# through this predicate and ONE flagged. Removing an agent's soul, moving her 18
# skills and unloading her launchd gateway all scored as conversation, because
# every one was `ssh den '<verb> ...'` and MUT anchors the verb to a LOCAL command
# boundary. Inside a quoted remote string there is no boundary before the verb.
# REMOTE_WRITE fixed this for API calls on 09-19 and left shell verbs behind.
#
# WHY THIS IS A SIBLING AND NOT A WIDER MUT. MUT is tuned for local shell and was
# NARROWED by operator ruling on 2026-09-02 because over-firing trained the
# reminder into noise. Unanchored `rm`/`mv` in MUT would match prose, heredoc
# bodies and `grep "rm x"`, and MUT is shared with owe_table — so widening it
# makes BOTH hooks louder. This matches only inside an ssh quoted region, and
# anchors the verb to that region's OWN command boundaries.
# 2026-09-20 REFUTED: this allowed exactly ONE token between ssh and the quote, so
# every `ssh -o ConnectTimeout=5 host '...'` missed. Measured against this estate's
# own 2044-line command-shape log: 207 of 668 ssh calls (31%) put a flag before the
# host -- and the widening was written to catch precisely those commands.
_REMOTE_Q = re.compile(
    r"(?:^|[;&|\n])\s*ssh\s+(?:-\w+(?:\s+[^\s'\"-]\S*)?\s+)*\S+\s+"
    r"('([^']*)'|\"([^\"]*)\")", re.S)
_REMOTE_VERB = re.compile(
    r"(?:^|[;&|\n])\s*"
    # 2026-09-20: a wrapper chain may sit between the boundary and the verb.
    # env assignments, then any stack of sudo/nohup/time/command/exec, then an
    # optional absolute path. Each token is BOUNDED and specific, so this cannot
    # slide the anchor over arbitrary text the way an unanchored verb would.
    r"(?:env\s+)?(?:\w+=(?:'[^']*'|\"[^\"]*\"|[^\s;&|]*)\s+)*"
    r"(?:(?:sudo|nohup|command|exec)(?:\s+-\w+(?:\s+[^\s-]\S*)?)*\s+|time\s+)*"
    r"(?:/\S*/)?"
    r"(?:rm|mv|cp|mkdir|rmdir|ln|chmod|chown|truncate|dd|tee"
    r"|launchctl\s+(?:load|unload|bootstrap|bootout|kickstart|remove)"
    r"|systemctl\s+\S+"
    r"|git\s+(?:-C\s+\S+\s+)?(?:commit|push|add|checkout|reset|merge|rebase|tag|revert))"
    r"\b")


def _strip_heredocs(cmd):
    """Remove heredoc BODIES before matching. A heredoc body is data being
    written, not commands being run.

    CAUGHT BY THE HOOK ITSELF, 2026-09-20, on the turn that shipped
    remote_mutation(). A latency test was a python heredoc whose body held the
    literal test case `"ssh den 'launchctl bootout gui/501/x'"`, and the
    new predicate flagged it as a build. Writing an EXAMPLE of a remote command
    is the single most common thing done in this estate's heredocs, so this
    would have fired on most authoring turns — the exact over-firing the
    2026-09-02 ruling narrowed MUT to stop.

    RESIDUAL MISS, STATED NOT HIDDEN: a heredoc piped into a remote shell
    (`ssh den 'bash -s' <<EOF ... rm -rf ... EOF`) no longer flags. That shape is
    rare here; a false alarm on every authoring turn is not. A guard trained
    into noise catches nothing at all.
    """
    # 2026-09-20 REFUTED: `<<-` exists to permit a TAB-INDENTED terminator and this
    # demanded column 0; \w+ rejected tags with a hyphen or dot (EOF-1, PY.1); and
    # CRLF put a \r before the newline, killing the opener.
    return re.sub(r"<<-?\s*['\"]?([\w.-]+)['\"]?\r?\n.*?^[ \t]*\1[ \t]*\r?$",
                  " <<heredoc> ", cmd, flags=re.S | re.M)


def _scrub(cmd):
    """Strip null sinks and temp buffers. Same rule as main()'s, extracted so the
    PreToolUse form cannot carry a second copy that drifts."""
    s = re.sub(r">>?\s*(/dev/null|/dev/stderr|&\d)", " ", cmd)
    return re.sub(r">>?\s*(/tmp|/private/tmp|\$TMPDIR)[^\s;&|]*", " ", s)


def _blank_quoted(text):
    """Replace the CONTENTS of quoted strings with spaces, keeping length.

    A verb or a `;` inside quotes is data. 2026-09-20 refuted:
        echo 'step one; make sure the daemon is up'   -> fired on `; make `
        grep -rn "ssh den 'rm -rf x'" ~/notes          -> fired
    Only the MUT/REMOTE_WRITE pass uses this. remote_mutation and wrapped_build
    must see inside quotes -- that is the whole point of them -- so they run
    FIRST, on the raw body."""
    quotes = ("'", chr(34))
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in quotes:
            j = text.find(c, i + 1)
            if j == -1:
                out.append(text[i:]); break
            out.append(c + " " * (j - i - 1) + c); i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


_LOCAL_Q = re.compile(
    r"(?:^|[;&|\n])\s*(?:bash|sh|zsh)\s+-\w*c\s+('([^']*)'|\"([^\"]*)\")"
    r"|(?:^|[;&|\n])\s*eval\s+('([^']*)'|\"([^\"]*)\")", re.S)


def wrapped_build(cmd):
    """A verb inside `bash -c '...'` / `sh -c "..."` / `eval '...'` is a real
    command, not data. Refuted 2026-09-20: all three returned False.

    The wrapper itself must sit at a command boundary, so quoting an EXAMPLE of
    one (`grep "bash -c 'git push'" notes`) still does not fire."""
    for m in _LOCAL_Q.finditer(cmd or ""):
        # groups 1 and 4 are the quoted forms INCLUDING their quotes; 2/3 and
        # 5/6 are the contents. Taking the outer form left a leading quote, so
        # MUT's boundary never matched and `eval "git push"` stayed quiet.
        g = m.groups()
        inner = next((x for i, x in enumerate(g) if x and i not in (0, 3)), "")
        if MUT.search(_scrub(inner)):
            return True
    return False


def remote_mutation(cmd):
    """True when a mutating shell verb runs INSIDE a quoted remote command.
    Scratch paths inside the remote string are stripped first, so
    `ssh den 'rm -f /tmp/x'` stays quiet exactly like its local equivalent."""
    for m in _REMOTE_Q.finditer(cmd or ""):
        inner = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        inner = _scrub(inner)
        inner = re.sub(r"\b(?:rm|mv|cp|truncate|tee|dd)\b[^;&|\n]*?"
                       r"(?:/tmp|/private/tmp|\$TMPDIR)[^\s;&|]*", " ", inner)
        if _REMOTE_VERB.search(inner):
            return True
    return False


def is_build_command(cmd):
    """THE single predicate. Both forms of the conductor call this one function:
    mark_build (PostToolUse, owes the table) and hook_prior_pre (PreToolUse, asks
    for the prior). Two copies would let the hooks disagree about whether a turn
    was a build, which is the drift this entry point exists to prevent."""
    if not cmd or is_notes(cmd):
        return False
    body = _strip_heredocs(cmd)
    scrubbed = _scrub(body)
    # The quoted-region checks look INSIDE quotes and must run on the raw body.
    # MUT must not: a `;` or a verb inside a quoted string is DATA, which is why
    # `echo 'step one; make sure the daemon is up'` fired. Blank the quoted
    # contents for the MUT pass only.
    if remote_mutation(body) or wrapped_build(body):
        return True
    bare = _blank_quoted(scrubbed)
    # REMOTE_WRITE RUNS ON THE RAW BODY, NEVER ON `bare`. It is a
    # quoted-region check by construction: its 09-19 rationale is that the
    # write travels INSIDE the quoted remote command
    #     ssh den 'python3 patch_registers.py NA'
    # and its tokens are deliberately UNANCHORED for that reason. Blanking
    # the quotes erases exactly what it exists to find. On 2026-09-21 it was
    # paired with MUT on `bare` while _blank_quoted was added for MUT's
    # false positives, which silently reopened the 09-19 hole: three remote
    # write shapes scored as conversation again, so no table was owed.
    return bool(MUT.search(bare) or REMOTE_WRITE.search(body))


def is_notes(text):
    """A notes path EXEMPTS only when nothing else in the command is a build.

    2026-09-20 REFUTED. STILL_A_BUILD listed just git and launchctl, while NOTES
    matches `/memory/` ANYWHERE -- including a trailing comment. So every other
    guard in this file was switchable off by typing `# /memory/`:
        terraform apply -auto-approve && echo done >> ~/memory/log.md  -> False
        docker push registry/img:latest # per /memory/plan              -> False
        pip install evilpkg  # noted in MEMORY.md                       -> False
        ssh den 'rm -rf ~/agent/soul' && echo gone >> ~/memory/log.md     -> False
    Nine for nine. The exemption now re-arms on the FULL build vocabulary."""
    if not text or not NOTES.search(text):
        return False
    return not (MUT.search(text) or REMOTE_WRITE.search(text) or remote_mutation(text))


def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    tool = d.get("tool_name", "")
    # Write/Edit no longer flag: authoring a file is not touching a repo.
    if tool != "Bash":
        return
    cmd = (d.get("tool_input") or {}).get("command", "") or ""
    # SCRATCH REDIRECTS ARE NOT CHANGES. Caught on this hook's second real turn:
    # a read-only monitoring pass flagged as a build because `>/dev/null` and a
    # `>/tmp/nv.txt` exit-code buffer both matched the redirect shape. Those
    # appear in nearly every probe, so the reminder would have fired on every
    # monitoring turn and been trained into noise - the precise failure this
    # hook exists to prevent. Strip null sinks and temp buffers before matching.
    if is_build_command(cmd):
        mark("Bash", _flags.sid(d))

def mark(what, session):
    # ONE FLAG PER CONSUMER, and this is why. A cold reader proved on
    # 2026-09-01 that owe_table.py CONSUMES the build flag, so whichever Stop
    # hook draws second sees nothing. Gate 08 had been firing on luck. Each
    # consumer now owns its own flag and cannot silence the other. Adding a
    # consumer means adding a flag here — a shared one reintroduces the bug.
    for name in ("build-turn", "prior-owed", "posterior-owed"):
        p = _flags.path(name, session)
        try:
            with open(p, "a") as f:
                f.write(what + "\n")
        except Exception as e:
            # D5 2026-09-20: this was `except Exception: pass`. A read-only or full
            # TMPDIR, or an id that could not form a filename, lost the table, the
            # prior AND the posterior with no signal whatsoever. A guard that fails
            # must say so; stderr reaches the hook log.
            sys.stderr.write("mark_build: could not write %s (%s)\n" % (p, e))

main()
