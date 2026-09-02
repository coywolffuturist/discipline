#!/usr/bin/env python3
"""bait_capture.py — capture.py, seen to refuse, seen to roll back, seen to land.

capture.py writes the MEMORY STORE. Two silent-corruption defects were found in
it by hand and fixed; neither fix had a bait. These run the real tool against a
throwaway store and read the store back after every call — a "wrote" that did
not land, or a memory file left behind after a failed index, is the defect.
"""
import io, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FORM = os.path.join(HERE, "capture.py")
LEDGER = "reference_coywolf_chunk_ledger.md"
PENDING = "\n---\n\n## Pending — named but NOT yet chunked"

bad = []
total = 0


def store(anchor=True, index_bytes=200):
    d = tempfile.mkdtemp(prefix="capture-bait-")
    io.open(os.path.join(d, LEDGER), "w", encoding="utf-8").write(
        "# ledger\n\n**OLD.** an old move\n" + (PENDING + "\n\n- pending thing\n" if anchor else "\n"))
    # The REAL header, with its suffix. A bait on a bare `# Memory Index` passed
    # an anchor the real file never matched.
    filler = "> filler line to size the index\n"
    body = "# Memory Index — the ROUTER\n\n" + filler * max(0, (index_bytes - 20) // len(filler))
    io.open(os.path.join(d, "MEMORY.md"), "w", encoding="utf-8").write(body)
    return d


def run(d, *args, env=None):
    e = dict(os.environ, COYWOLF_MEMORY_DIR=d) if d else dict(os.environ)
    if d is None:
        e.pop("COYWOLF_MEMORY_DIR", None)
    e.update(env or {})
    r = subprocess.run([sys.executable, FORM] + list(args), capture_output=True, text=True,
                       env=e, timeout=30)
    return r.returncode, r.stdout + r.stderr


def bait(label, cond, detail=""):
    global total
    total += 1
    first = detail.strip().splitlines()[0] if detail.strip() else ""
    print("  %s %-62s %s" % ("ok " if cond else "XX ", label, first[:40]))
    if not cond:
        bad.append(label)


def read(d, name):
    return io.open(os.path.join(d, name), encoding="utf-8").read()


WB = ("writeback", "the bait memory", "a description", "--kind", "feedback",
      "--body", "the body", "--index", "[The bait memory](feedback_the_bait_memory.md) — hook")
MEMFILE = "feedback_the_bait_memory.md"

# gate 16 — chunk
d = store()
rc, out = run(d, "chunk", "The move", "what it did")
led = read(d, LEDGER)
bait("BAIT K1 chunk lands ABOVE the Pending anchor", rc == 0 and "chunked" in out
     and led.index("**THE MOVE.**") < led.index("## Pending"), out)
shutil.rmtree(d)
d = store(anchor=False)
before = read(d, LEDGER)
rc, out = run(d, "chunk", "The move", "what it did")
bait("BAIT K2 a ledger with no anchor is REFUSED, ledger untouched",
     rc == 1 and "anchor is missing" in out and read(d, LEDGER) == before, out)
shutil.rmtree(d)

# gate 17 — writeback
d = store()
rc, out = run(d, *WB)
bait("BAIT K3 writeback writes the file AND the index line",
     rc == 0 and os.path.exists(os.path.join(d, MEMFILE)) and "[The bait memory]" in read(d, "MEMORY.md"), out)
rc, out = run(d, *WB)
bait("BAIT K4 a second writeback of the same name is refused as a duplicate",
     rc == 1 and "already exists" in out, out)
shutil.rmtree(d)
d = store()
rc, out = run(d, "writeback", "x", "y", "--kind", "musing", "--body", "b", "--index", "i")
bait("BAIT K5 an unknown kind is refused before anything is written",
     rc == 1 and "kind must be" in out and not [f for f in os.listdir(d) if f.startswith("musing")], out)
shutil.rmtree(d)
d = store(index_bytes=24000)
rc, out = run(d, *WB)
bait("BAIT K6 an index at budget REFUSES the entry", rc == 1 and "budget" in out, out)
bait("BAIT K7 ...and the memory file is ROLLED BACK, not orphaned", not os.path.exists(os.path.join(d, MEMFILE)))
bait("BAIT K8 ...and the index was not truncated", len(read(d, "MEMORY.md").encode("utf-8")) >= 23900)
shutil.rmtree(d)
d = store()
os.remove(os.path.join(d, "MEMORY.md")); os.makedirs(os.path.join(d, "MEMORY.md"))
rc, out = run(d, *WB)
bait("BAIT K9 an unreadable index fails the whole act and removes the file",
     rc == 1 and "Nothing was kept" in out and "was removed" in out
     and not os.path.exists(os.path.join(d, MEMFILE)), out)
shutil.rmtree(d)

# store discovery — evidence, not order
h = tempfile.mkdtemp(prefix="capture-home-")
for name in ("aaa", "bbb"):
    m = os.path.join(h, ".claude", "projects", name, "memory"); os.makedirs(m)
    io.open(os.path.join(m, LEDGER), "w", encoding="utf-8").write("x" + PENDING + "\n")
rc, out = run(None, "chunk", "t", "b", env={"HOME": h})
bait("BAIT K10 two candidate stores holding the ledger: REFUSE, do not guess",
     rc == 1 and "cannot identify the store" in out, out)
shutil.rmtree(h)
h = tempfile.mkdtemp(prefix="capture-home-")
rc, out = run(None, "chunk", "t", "b", env={"HOME": h})
bait("BAIT K11 no store at all: refuse with the override named", rc == 1 and "COYWOLF_MEMORY_DIR" in out, out)
shutil.rmtree(h)

# THE DOCUMENTED CORRUPTION, reproduced: a size limit standing in for a full
# disk. A reviewer showed on 2026-09-02 that with the atomic write replaced by
# a plain open("w") every bait above stayed green while the ledger was
# truncated to 1024 bytes and the tool printed "chunked". This is the bait
# for that, and it must be the FIRST thing anyone touching _atomic_write sees.
import resource
d = store()
before = read(d, LEDGER)
def _cap():
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024, 1024))
r = subprocess.run([sys.executable, FORM, "chunk", "Big move", "x" * 3000], capture_output=True,
                   text=True, env=dict(os.environ, COYWOLF_MEMORY_DIR=d), preexec_fn=_cap, timeout=30)
bait("BAIT K12 a write that cannot complete REFUSES (rc 1) rather than reporting chunked",
     r.returncode == 1 and "NOTHING was changed" in (r.stdout + r.stderr), r.stdout + r.stderr)
bait("BAIT K13 ...and the ledger is byte-for-byte intact, not truncated", read(d, LEDGER) == before,
     "%d -> %d bytes" % (len(before), len(read(d, LEDGER))))
shutil.rmtree(d)

d = store()
rc, out = run(d, *WB)
idx = read(d, "MEMORY.md")
bait("BAIT K14 the index line lands directly under the REAL header, not above it or at the end",
     rc == 0 and idx.index("# Memory Index") < idx.index("[The bait memory]") < idx.index("> filler"), idx[:60])
shutil.rmtree(d)

# The budget boundary, exactly. A reviewer moved the check 40 bytes and every
# bait stayed green. Here the index is sized so the entry lands EXACTLY on the
# budget, and then one byte past it.
line = "> " + WB[-1].strip() + "\n"
for slack, want_rc, label in ((0, 0, "K15 an entry that reaches the budget exactly lands"),
                              (1, 1, "K16 an entry that passes the budget by one byte is refused")):
    d = store(index_bytes=100)
    base = read(d, "MEMORY.md")
    target = 24000 - len(line.encode("utf-8")) + slack
    body = base + "p" * (target - len(base.encode("utf-8")))
    io.open(os.path.join(d, "MEMORY.md"), "w", encoding="utf-8").write(body)
    rc, out = run(d, *WB)
    bait("BAIT " + label, rc == want_rc, "index %d bytes, rc=%s" % (len(body.encode("utf-8")), rc))
    shutil.rmtree(d)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
