#!/usr/bin/env python3
"""capture — append to the durable stores, correctly, in one command.

Shared code form for gate 16 (chunk-it) and gate 17 (write-back). Two gates, one
tool, different subcommands: each gate reports its own row and neither hides
inside the other's.

WHY IT EXISTS. Both gates fire at the end of a turn and both are satisfied by an
APPEND. Until now every append was a hand-written python heredoc — roughly ten of
them in one day, each re-deriving the anchor, the escaping and the file layout.
That is the compile-it trigger met several times over, and hand-written appends
had already produced one silent failure: a chunk reported as appended that was
not.

WHAT IT DOES NOT DO. It does not decide whether something is worth capturing.
That judgement is the gate; this is only the hands.
"""
import argparse, io, os, re, sys, tempfile

LEDGER_NAME = "reference_coywolf_chunk_ledger.md"

# THE STORE IS DISCOVERED, NEVER HARDCODED.
#
# This file previously hardcoded an absolute path under ~/.claude/projects/
# containing the operator's ACCOUNT NAME, in a public repository. A reviewer
# found it before the commit was pushed. The estate's leak gate exists for
# exactly this, and it was not run against this repo.
#
# Order: an explicit override, then the single memory directory under
# ~/.claude/projects/. If there is more than one, REFUSE rather than guess —
# writing a memory to the wrong store is silent and permanent.
def _memdir():
    env = os.environ.get("COYWOLF_MEMORY_DIR")
    if env:
        return os.path.expanduser(env)
    import glob
    cand = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/memory")))
    # Disambiguate on EVIDENCE, not on order: the real store is the one already
    # holding the ledger this tool appends to. Seven directories match the glob
    # on the primary workstation, so picking the first would have been a guess
    # that writes to the wrong store silently.
    real = [d for d in cand if os.path.exists(os.path.join(d, LEDGER_NAME))]
    if len(real) == 1:
        return real[0]
    if not cand:
        sys.exit("capture: no memory store found. Set COYWOLF_MEMORY_DIR.")
    sys.exit("capture: cannot identify the store (%d candidates, %d hold %s). "
             "Set COYWOLF_MEMORY_DIR." % (len(cand), len(real), LEDGER_NAME))


MEMDIR = _memdir()
LEDGER = os.path.join(MEMDIR, LEDGER_NAME)
INDEX = os.path.join(MEMDIR, "MEMORY.md")
PENDING = "\n---\n\n## Pending — named but NOT yet chunked"



def _atomic_write(path, text):
    """Write via a temp file and os.replace. NEVER truncate the real file.

    `io.open(path, "w").write(text)` TRUNCATES FIRST and flushes in __del__,
    where an OSError is raised during finalization and SILENTLY IGNORED by the
    interpreter. A reviewer reproduced it with a size limit standing in for a
    full disk: MEMORY.md went from 8,616 bytes to 512, the tool printed
    "wrote / indexed", and exited 0. The rollback never ran because the
    exception never reached it.

    A partial write that reports success is worse than a crash. os.replace is
    atomic on POSIX: the original survives untouched until the new content is
    complete on disk.
    """
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".capture-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())     # the error must surface HERE, not in __del__
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

def chunk(title, body):
    """Gate 16. Append a named move to the ledger, above the Pending section."""
    s = io.open(LEDGER, encoding="utf-8").read()
    if PENDING not in s:
        sys.exit("capture: the ledger's Pending anchor is missing — refusing to guess where to append")
    entry = "\n**%s** %s\n" % (title.rstrip(".").upper() + ".", body.strip())
    before = len(s)
    s = s.replace(PENDING, entry + PENDING, 1)
    # chunk() previously had NO error handling whatsoever. The same size-limit
    # test truncated a 7,257-byte ledger to 512 bytes and reported success.
    try:
        _atomic_write(LEDGER, s)
    except Exception as e:
        sys.exit("capture: the ledger could not be written (%s). NOTHING was "
                 "changed — the original is intact." % e)
    # VERIFY the write. A hand-written append was once reported as landed when it
    # had not, so this reads the file back rather than trusting the call.
    after = io.open(LEDGER, encoding="utf-8").read()
    if title.rstrip(".").upper() not in after:
        sys.exit("capture: append did NOT land — the ledger is unchanged")
    print("chunked: %s  (+%d bytes)" % (title[:60], len(after) - before))


def writeback(name, description, kind, body, index_line):
    """Gate 17. Write a memory file and index it in one act.

    Both halves or neither: an unindexed memory file is not retrievable, which is
    the whole point of writing it. A file written and never indexed is the
    'structure without a reader' failure this estate has recorded before."""
    if kind not in ("user", "feedback", "project", "reference"):
        sys.exit("capture: kind must be one of user | feedback | project | reference")
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    path = os.path.join(MEMDIR, "%s_%s.md" % (kind, slug.replace("-", "_")))
    if os.path.exists(path):
        sys.exit("capture: %s already exists — update it rather than creating a duplicate" % path)
    # BOTH HALVES OR NEITHER, AND THIS IS THE MECHANISM, NOT THE INTENT.
    #
    # The first version wrote the memory file, then the index. A reviewer made
    # the index unwritable: the file was created, the index write threw an
    # uncaught traceback, and the verification block below never ran because it
    # sits AFTER the throwing line. The result was an orphaned memory file — the
    # exact "structure without a reader" state gate 17 says is impossible — and
    # the tool's own duplicate guard then blocked every retry. Permanent, by the
    # guard meant to protect it.
    #
    # So: write the file, and if ANYTHING after that fails, REMOVE it. A rollback
    # is the only thing that makes "or neither" true.
    body_txt = ("---\nname: %s\ndescription: %s\nmetadata:\n  type: %s\n---\n\n%s\n"
                % (slug, description, kind, body.strip()))
    _atomic_write(path, body_txt)
    try:
        idx = io.open(INDEX, encoding="utf-8").read()
        line = "> %s\n" % index_line.strip()

        # THE INDEX HAS A BUDGET AND THIS IS WHERE IT IS ENFORCED.
        #
        # MEMORY.md is loaded at session start and TRUNCATED past ~24400 bytes.
        # It sat 6,491 bytes over for weeks: 53 entries were silently never
        # loaded, costing bytes and delivering nothing. The session-start hook
        # warned every single session and the warning was ignored every single
        # session — a guard that only warns is a guard that gets ignored.
        #
        # So the refusal lives at the WRITE point, where the person adding an
        # entry is the person who can prune one. It refuses; it never truncates.
        BUDGET = 24000
        projected = len(idx.encode("utf-8")) + len(line.encode("utf-8"))
        if projected > BUDGET:
            raise IOError(
                "MEMORY.md would reach %d bytes, past the %d-byte session loader "
                "budget. Entries past the limit are silently NOT LOADED. Move a "
                "lookup-type entry to INDEX.md before adding a router-type one — "
                "MEMORY.md carries what must fire UNPROMPTED, INDEX.md carries "
                "what answers a question you already have." % (projected, BUDGET))
        if line not in idx:
            # The header is `# Memory Index — the ROUTER`, not `# Memory Index`.
            # The first anchor was the bare string with a newline on each side,
            # which the real file has never contained, so every entry landed
            # ABOVE the header. A bait built on the real header caught it on
            # 2026-09-02. Match the header LINE, then insert under it.
            m = re.search(r"^# Memory Index[^\n]*\n\n?", idx, re.M)
            if m:
                idx = idx[:m.end()] + line + idx[m.end():]
            else:
                idx = line + idx
            _atomic_write(INDEX, idx)
        if not os.path.exists(path) or line not in io.open(INDEX, encoding="utf-8").read():
            raise IOError("file or index entry did NOT land")
    except Exception as e:
        try:
            os.remove(path)
            undone = "the memory file was removed"
        except OSError:
            undone = "AND THE MEMORY FILE COULD NOT BE REMOVED: %s" % path
        sys.exit("capture: the index could not be written (%s). Nothing was kept — %s."
                 % (e, undone))
    print("wrote: %s\nindexed: %s" % (os.path.basename(path), index_line[:70]))


def main():
    ap = argparse.ArgumentParser(description="gate 16 / gate 17 — append to the durable stores")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("chunk", help="gate 16: append a named move to the ledger")
    c.add_argument("title"); c.add_argument("body")
    w = sub.add_parser("writeback", help="gate 17: write a memory file AND index it")
    w.add_argument("name"); w.add_argument("description")
    w.add_argument("--kind", required=True)
    w.add_argument("--body", required=True)
    w.add_argument("--index", required=True, help="the one-line MEMORY.md pointer")
    a = ap.parse_args()
    if a.cmd == "chunk":
        chunk(a.title, a.body)
    else:
        writeback(a.name, a.description, a.kind, a.body, a.index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
