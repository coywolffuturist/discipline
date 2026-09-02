#!/usr/bin/env python3
"""quotes — every quoted artifact and every count in a GATE.md must be IN THE RECORD.

WHY THIS EXISTS. A refuter found TWELVE false claims across eight gate files on
2026-09-01, hours before they would have published. The counts were right — I had
run those. The QUOTES were wrong, because I reconstructed them from the session
instead of reading the corpus:

  * a composite of two rows presented as one quote (gate 12)
  * a posterior recorded as "0.4 -> 0.8" reported as 0.4, inside the gate whose
    whole read is that a posterior is the prior MOVED (gate 19)
  * a BLOCKED row cited twice as the gate's own self-disproof, which exists
    nowhere in the 647-row corpus (gate 19)
  * "every N/A cites the same words" where 1 of 3, and 0 of 12, did (gates 10, 15)

ONE FAULT, not twelve: I ran the numbers and recalled the prose. So this checks
the prose the way I already checked the numbers.

It is deliberately NARROW. It verifies that a block quote corresponds to a real
artifact and that a stated count matches the corpus. It cannot check a
superlative ("the most consistently fired gate") — those must be computed, and
the report prints the true ranking so the claim can be written from evidence.
"""
import io, os, re, sys, collections

CORPUS = os.path.expanduser("~/.coywolf/gate-corpus")
GATES = "gates"
# Files a GATE.md may legitimately quote that are not the firing corpus.
OTHER_SOURCES = [os.path.expanduser("~/.git-hooks/pre-push"),
                 os.path.expanduser("~/.git-hooks/commit-msg")]


def rows():
    src = None
    for f in sorted(os.listdir(CORPUS)):
        if f.startswith("firings-") and f.endswith(".tsv"):
            src = os.path.join(CORPUS, f)
    if not src:
        print("quotes: UNVERIFIED — no firings-*.tsv in %s. A missing corpus is not a pass." % CORPUS)
        sys.exit(2)
    out = []
    for line in io.open(src, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) == 5 and p[0] != "ts":
            out.append(p)
    return out


def norm(s):
    s = re.sub(r"(?m)^\s*#+ ?", "", s)   # source files quote from COMMENTS
    s = re.sub(r"\*\*|\*|`|_", "", s)
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[—–]", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower().rstrip(".")


def quotes_in(text):
    """Block quotes, reflowed. A quote may span lines; a blank '>' separates them."""
    out, cur = [], []
    for line in text.splitlines():
        if line.startswith(">"):
            body = line[1:].strip()
            if body:
                cur.append(body)
            elif cur:
                out.append(" ".join(cur)); cur = []
        elif cur:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def main():
    R = rows()
    arts = [norm(r[4]) for r in R]
    by_name = collections.defaultdict(collections.Counter)
    for r in R:
        by_name[r[2]][r[3]] += 1

    bad, notes = [], []
    for g in sorted(os.listdir(GATES)):
        p = os.path.join(GATES, g, "GATE.md")
        if not os.path.exists(p):
            continue
        name = g.split("-", 1)[1]
        t = io.open(p, encoding="utf-8").read()

        # 1. every block quote must trace to ONE real source.
        #
        # Not an exact match: this repo is PUBLIC, so quotes from the private
        # record are deliberately scrubbed (a machine name becomes "one
        # machine"). A scrub is legitimate; a COMPOSITE of two rows is not, and
        # neither is an invented quote. So the test is best-single-row overlap.
        # A composite fails because no ONE row covers it, which is exactly the
        # defect that shipped in gate 12.
        for q in quotes_in(t):
            n = norm(q)
            if len(n) < 25:
                continue
            qt = set(n.split())
            best, score = "", 0.0
            for a in arts:
                at = set(a.split())
                ov = len(qt & at) / max(1, len(qt))
                if ov > score:
                    score, best = ov, a
            if score >= 0.98:
                continue                       # verbatim
            # NUMBERS ARE NEVER A SCRUB. A quote may be genericised for a public
            # repo; it may not carry a number the source does not. This exists
            # because a recorded posterior of "0.4 -> 0.8" was quoted as 0.4,
            # inside the gate whose read is that a posterior is the prior MOVED,
            # and a 74% scrub note was not enough to stop it shipping.
            qn = set(re.findall(r"\d+(?:\.\d+)?", n))
            bn = set(re.findall(r"\d+(?:\.\d+)?", best))
            if score >= 0.70 and (qn ^ bn):
                extra, missing = sorted(qn - bn), sorted(bn - qn)
                why = []
                if extra:
                    why.append("carries %s, not in the source" % ", ".join(extra))
                if missing:
                    # A DROPPED number is the worse half. "Durability 0.4 -> 0.8"
                    # quoted as 0.4 turned a posterior back into its prior.
                    why.append("DROPS %s from the source" % ", ".join(missing))
                bad.append("%s: quote %s: %r" % (g, "; ".join(why), q[:70]))
                continue
            if score >= 0.70:
                # A scrub. Legitimate, but SHOW it — a silent near-match is how
                # 0.4 got reported where the record said "0.4 -> 0.8".
                drift = sorted(qt - set(best.split()))
                notes.append("%s: quote is scrubbed/adapted (%.0f%% of one row). "
                             "Words not in the source: %s" % (g, score * 100, ", ".join(drift[:8])))
                continue
            if any(n in norm(io.open(f, encoding="utf-8", errors="replace").read())
                   for f in OTHER_SOURCES if os.path.exists(f)):
                continue                       # quoted from a named non-corpus source
            bad.append("%s: quote traces to NO single source (best row %.0f%%): %r"
                       % (g, score * 100, q[:80]))

        # 2. every "N FIRED" / "N N/A" / "N BLOCKED" must match this gate's counts
        c = by_name.get(name, {})
        for num, state in re.findall(r"\*\*(\d+) (FIRED|N/A|BLOCKED)", t) + \
                          re.findall(r"\b(\d+) (FIRED|N/A|BLOCKED)\b", t):
            if c.get(state, 0) != int(num):
                bad.append("%s: claims %s %s; the record has %d"
                           % (g, num, state, c.get(state, 0)))

    print("quotes: %d gate file(s) checked against %d corpus rows" % (len(os.listdir(GATES)), len(R)))
    if bad:
        print("\033[31mFAIL\033[0m  quotes — %d unsupported claim(s):" % len(bad))
        for b in bad:
            print("      " + b)
    else:
        print("\033[32mPASS\033[0m  quotes — every quoted artifact and count traces to the record")
    for nt in notes:
        print("      note: " + nt)

    # Superlatives cannot be checked, only computed. Print the truth so the
    # claim gets written from evidence instead of from impression.
    rank = sorted(((sum(v.values()) and v.get("FIRED", 0) / sum(v.values()), v.get("FIRED", 0), k)
                   for k, v in by_name.items()), reverse=True)[:5]
    print("      FYI, true FIRED ranking (rate, count): "
          + " · ".join("%s %.3f/%d" % (k, r, n) for r, n, k in rank))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
