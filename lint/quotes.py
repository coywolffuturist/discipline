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
import difflib, io, os, re, sys, collections

# QUOTES_CORPUS lets the bait point the REAL file at a throwaway corpus. The
# bait used to rewrite this line in a copy, which meant the file that was
# seen red was never the file that ships.
CORPUS = os.environ.get("QUOTES_CORPUS") or os.path.expanduser("~/.coywolf/gate-corpus")
GATES = "gates"
# Files a GATE.md may legitimately quote that are not the firing corpus.
OTHER_SOURCES = [os.path.expanduser("~/.git-hooks/pre-push"),
                 os.path.expanduser("~/.git-hooks/commit-msg")]


def rows():
    src = None
    if not os.path.isdir(CORPUS):
        # SKIPPED, not failed. The firing corpus is private estate state; a
        # stranger cannot have it, and refusing their build for that is a false
        # denial. Saying nothing would be worse — a green that means unchecked.
        print("quotes: SKIPPED — no firing corpus at %s. Quotes and counts in the "
              "gate files are UNVERIFIED on this machine, not verified." % CORPUS)
        sys.exit(2)
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
        if line.lstrip().startswith(">"):   # indented blockquotes are blockquotes
            body = line.lstrip()[1:].strip()
            if body:
                cur.append(body)
            elif cur:
                out.append(" ".join(cur)); cur = []
        elif cur:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def inline_quotes(text):
    """Quotations that sit inside a sentence: *"..."* and plain "...".

    Only spans long enough to be a real quotation, and only those with a
    sentence's shape — a short quoted term is a name, not a citation."""
    out = []
    # Straight AND typographic quotes. A reviewer slipped a wholly fabricated
    # citation through in curly quotes because only `"` was matched.
    for pat in (r'[*`]?"([^"\n]{40,})"[*`]?', u'[*`]?\u201c([^\u201d\n]{40,})\u201d[*`]?'):
        for m in re.finditer(pat, text):
            out.append(m.group(1))
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

        # 1. every quotation must trace to ONE real source.
        #
        # INLINE ones too. The first version read only lines starting with ">",
        # so three findings hid in italic and backticked quotations mid-sentence
        # — including a "verbatim" claim that misquoted the source it named.
        #
        # Not an exact match: this repo is PUBLIC, so quotes from the private
        # record are deliberately scrubbed (a machine name becomes "one
        # machine"). A scrub is legitimate; a COMPOSITE of two rows is not, and
        # neither is an invented quote. So the test is best-single-row overlap.
        # A composite fails because no ONE row covers it, which is exactly the
        # defect that shipped in gate 12.
        blocks = quotes_in(t)
        for q in blocks + inline_quotes(t):
            n = norm(q)
            if len(n) < 25:
                continue
            # An INLINE quotation is only judged when it NEARLY matches a source.
            # A block quote claims to cite; an inline one may simply be the
            # author's own emphasis, and failing those would train this check
            # into noise within a day. A near-miss is the real defect: it means
            # a source was named and then misquoted.
            inline = q not in blocks
            # SEQUENCE, not SET. The first version compared word SETS, so a
            # reviewer reversed gate 04's central finding — "split custody meant
            # no shared write path" -> "NO split custody meant shared write
            # path" — and it scored 1.0 and reported "verbatim". Set-identical,
            # meaning inverted. Order is the whole content of a sentence.
            qw = n.split()
            best, score = "", 0.0
            for a in arts:
                r = difflib.SequenceMatcher(None, qw, a.split()).ratio()
                if r > score:
                    score, best = r, a
            # NO EARLY EXIT ON SIMILARITY. This used to `continue` at >= 0.98
            # before the number, negation and drop rules ran. On a 45-word
            # corpus row, DELETING one word scores 0.989 — so "the synthesis is
            # NOT in the ledger" quoted as "the synthesis IS in the ledger"
            # passed silently as verbatim. High similarity is exactly where a
            # meaning inversion hides; it is the least safe place to stop
            # checking. The rules below run first, and `verbatim` is decided
            # after them.
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
            # DROPPED MATERIAL. A pure subset scored 89% and passed as a
            # "scrub": gate 12's quote had lost "Only you can confirm", which is
            # the evidence its whole argument rests on. Genericising a name is a
            # scrub; deleting a clause is a different quotation.
            bw = best.split()

            # PADDING, the mirror of dropping. A fabricated clause APPENDED to a
            # real quote keeps similarity high and passed as a scrub — which is
            # the more dangerous direction, because the invented half inherits
            # the credibility of the real half.
            if score >= 0.70 and len(qw) > len(bw) * 1.15:
                bad.append("%s: quote ADDS %d words its source row does not have: %r"
                           % (g, len(qw) - len(bw), q[:70]))
                continue

            # NEGATION POSITION. Sequence similarity cannot see a meaning
            # inversion: moving one word scored 92% when a reviewer turned
            # "split custody meant NO shared write path" into "NO split custody
            # meant shared write path". Same words, opposite claim, small edit.
            #
            # So each negation in the quote must be followed by the same word it
            # is followed by in the source. That is what a reversal breaks and a
            # genericising scrub does not.
            NEG = {"no", "not", "never", "without", "cannot", "nothing", "none"}
            def _negpairs(ws):
                return {(w, ws[i + 1]) for i, w in enumerate(ws[:-1]) if w in NEG}
            qneg, bneg = _negpairs(qw), _negpairs(bw)
            # SYMMETRIC. `qneg - bneg` catches a negation MOVED or ADDED and is
            # blind to one DELETED — which is the cleaner inversion: drop "not"
            # and the sentence asserts the opposite at 0.98 similarity.
            if score >= 0.70 and (qneg ^ bneg):
                bad.append("%s: negation differs from the source (quote %s / source %s): %r"
                           % (g, sorted(qneg) or "[]", sorted(bneg) or "[]", q[:60]))
                continue
            if score >= 0.70 and len(qw) < len(bw) * 0.85:
                bad.append("%s: quote DROPS %d of %d words from its source row: %r"
                           % (g, len(bw) - len(qw), len(bw), q[:70]))
                continue
            if score >= 0.98:
                continue                       # verbatim, and it survived the rules
            if score >= 0.70:
                # A scrub. Legitimate, but SHOW it — a silent near-match is how
                # 0.4 got reported where the record said "0.4 -> 0.8".
                drift = sorted(set(qw) - set(bw))
                notes.append("%s: quote is scrubbed/adapted (%.0f%% of one row). "
                             "Words not in the source: %s" % (g, score * 100, ", ".join(drift[:8])))
                continue
            # Other named sources, matched the same way: near-miss = misquote.
            for f in OTHER_SOURCES:
                if not os.path.exists(f):
                    continue
                ftxt = norm(io.open(f, encoding="utf-8", errors="replace").read())
                if n in ftxt:
                    score = 1.0
                    break
                fw = ftxt.split()
                for i in range(0, max(1, len(fw) - len(qw)), 5):
                    r = difflib.SequenceMatcher(None, qw, fw[i:i + len(qw) + 5]).ratio()
                    if r > score:
                        score, best = r, " ".join(fw[i:i + len(qw) + 5])
            if score >= 0.98:
                continue
            # An inline quote is normally the author's own emphasis, so a low
            # score means "not a citation" and passes. UNLESS the sentence
            # ATTRIBUTES it to the record — then a low score means a fabricated
            # citation, which is the worst thing this checker exists to catch.
            # A reviewer walked a wholly invented quotation through in
            # typographic quotes, attributed to "the operator's own words".
            if inline and score < 0.70:
                where = t[max(0, t.find(q) - 220): t.find(q) + len(q) + 80].lower()
                claims_source = re.search(
                    r"the record|the corpus|the log|verbatim|own words|firing|"
                    r"recorded|the ruling|reads?:|states?:", where)
                if not claims_source:
                    continue                   # the author's own words, not a citation
            bad.append("%s: %s traces to NO single source (best %.0f%%): %r"
                       % (g, "inline quote" if inline else "quote", score * 100, q[:80]))

        # 2. every "N FIRED" / "N N/A" / "N BLOCKED" must match this gate's counts
        c = by_name.get(name, {})
        # ATTRIBUTION. The first version credited every "<n> <STATE>" in a file
        # to that file's own gate, so a TRUE statement about a neighbour —
        # "disprove-first ran 38 FIRED" — was reported as fabricated. A count is
        # only this gate's if no other gate is named in the same sentence.
        others = set(by_name) - {name}
        for sent in re.split(r"(?<=[.!?])\s+|\n\n", t):
            # WORD BOUNDARY. Plain `in` matched "ste" inside "estate" and
            # attributed gate 04's own counts to gate 01.
            # sorted(), because `others` is a SET and Python randomizes set
            # iteration per process. Taking named[0] made this check return RED
            # or GREEN on identical bytes depending on PYTHONHASHSEED — a
            # build-gating check whose verdict was a coin flip.
            named = sorted(o for o in others
                           if re.search(r"\b%s\b" % re.escape(o), sent))
            for num, state in re.findall(r"\b(\d+) (FIRED|N/A|BLOCKED)\b", sent):
                if named:
                    real = by_name.get(named[0], {})
                    if real.get(state, 0) != int(num):
                        bad.append("%s: says %s has %s %s; the record has %d"
                                   % (g, named[0], num, state, real.get(state, 0)))
                elif c.get(state, 0) != int(num):
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
