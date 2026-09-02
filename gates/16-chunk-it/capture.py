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
import argparse, io, os, re, sys

LEDGER = os.path.expanduser(
    "~/.claude/projects/-Users-brendanjoyce/memory/reference_coywolf_chunk_ledger.md")
MEMDIR = os.path.expanduser("~/.claude/projects/-Users-brendanjoyce/memory")
INDEX = os.path.join(MEMDIR, "MEMORY.md")
PENDING = "\n---\n\n## Pending — named but NOT yet chunked"


def chunk(title, body):
    """Gate 16. Append a named move to the ledger, above the Pending section."""
    s = io.open(LEDGER, encoding="utf-8").read()
    if PENDING not in s:
        sys.exit("capture: the ledger's Pending anchor is missing — refusing to guess where to append")
    entry = "\n**%s** %s\n" % (title.rstrip(".").upper() + ".", body.strip())
    before = len(s)
    s = s.replace(PENDING, entry + PENDING, 1)
    io.open(LEDGER, "w", encoding="utf-8").write(s)
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
    io.open(path, "w", encoding="utf-8").write(
        "---\nname: %s\ndescription: %s\nmetadata:\n  type: %s\n---\n\n%s\n"
        % (slug, description, kind, body.strip()))
    idx = io.open(INDEX, encoding="utf-8").read()
    line = "> %s\n" % index_line.strip()
    if line not in idx:
        anchor = "\n# Memory Index\n"
        if anchor in idx:
            idx = idx.replace(anchor, anchor + "\n" + line, 1)
        else:
            idx = line + idx
        io.open(INDEX, "w", encoding="utf-8").write(idx)
    if not os.path.exists(path) or line not in io.open(INDEX, encoding="utf-8").read():
        sys.exit("capture: file or index entry did NOT land")
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
