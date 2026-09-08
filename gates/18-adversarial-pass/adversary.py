#!/usr/bin/env python3
"""adversary.py — gate 18's CONTINUOUS form, and the wire to gate 19's ledger.

Gate 18 fires ONCE, at the end, on a finished claim. It catches a wrong
CONCLUSION. It does not catch a wrong PROCESS, and on 2026-09-07 a single
session produced seven process errors and almost no wrong conclusions: a false
"deleted", a silently dropped argument, a corrupt refusal string, a lock that
invalidated itself and spent his quota, two baits that covered nothing, and a
bait appended below its own sys.exit. Gate 18 read BLOCKED twice that day
because nothing outward-facing fired it, so no refuter ran at all while all
seven went past.

So gate 18 gets a second form: an adversary woken with each ARTIFACT as it
lands, scoring how easily it can be broken. Adapted from bajpainaman/solve,
whose adversary watches a directory and messages the owner at score >= 7. Ours
is woken on demand instead of polling, because a poller burns tokens while
nothing is happening and his quota is the constraint we keep hitting.

THE PART THAT IS OURS. His adversary writes a score and nothing reads it; his
calibration ledger scores claims and never sees the adversary. Here the score is
carried onto the posterior it attacked, so `posterior.py audit` can eventually
answer: DOES A HIGH ADVERSARY SCORE PREDICT A CLAIM THAT SETTLES WRONG? If it
does, the score earns weight. If it does not, this whole form is theatre and
gets cut on evidence rather than on taste.

  adversary.py open <label>                         -> run id
  adversary.py record <run> <artifact> <score> <attack> [attack ...]
  adversary.py summary [run]
  adversary.py max <run>                            -> the highest score, for posterior.py --adv
"""
import json, math, os, sys, time, uuid

STATE = os.path.expanduser(os.environ.get("ADVERSARY_STATE", "~/.claude/state"))
LEDGER = os.path.join(STATE, "adversary.jsonl")
INTERRUPT = 7


class Corrupt(Exception):
    """FAIL CLOSED. A ledger that will not parse is never read as an empty ledger."""


class Refused(Exception):
    pass


def _entries():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for n, line in enumerate(open(LEDGER, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception as ex:
            raise Corrupt("adversary ledger line %d is not JSON: %s" % (n, ex))
        s = e.get("score")
        if isinstance(s, bool) or not isinstance(s, (int, float)) or not math.isfinite(s) \
           or not 0 <= s <= 10:
            raise Corrupt("adversary ledger line %d has a non-score: %r" % (n, s))
        out.append(e)
    return out


def _append(rec):
    os.makedirs(STATE, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def open_run(label):
    label = str(label).strip()[:120]
    if len(label) < 4:
        raise Refused("name the build — an unlabelled run cannot be read back")
    run = uuid.uuid4().hex[:8]
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "run": run, "event": "open",
             "label": label, "score": 0, "artifact": "", "attacks": []})
    return run


def record(run, artifact, score, attacks):
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 10:
        raise Refused("score must be an int 0..10 (10 = I can break this easily), got %r" % (score,))
    artifact = str(artifact).strip()
    if not artifact:
        raise Refused("name the artifact attacked")
    attacks = [str(a).strip() for a in attacks if str(a).strip()]
    if not attacks:
        raise Refused("an attack that names nothing is not an attack — give at least one")
    if any(len(a) < 12 for a in attacks):
        raise Refused("each attack must say something specific (>= 12 chars)")
    if not [e for e in _entries() if e.get("run") == run and e.get("event") == "open"]:
        raise Refused("no open run %r — call `adversary.py open <label>` first" % run)
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "run": run, "event": "attack",
             "artifact": artifact[:300], "score": score, "attacks": [a[:400] for a in attacks]})
    if score >= INTERRUPT:
        return ("INTERRUPT (score %d >= %d): %s\n  %s" %
                (score, INTERRUPT, artifact, "\n  ".join(attacks)))
    return "recorded %d — %s" % (score, artifact)


def max_score(run):
    hits = [e["score"] for e in _entries() if e.get("run") == run and e.get("event") == "attack"]
    return max(hits) if hits else 0


def summary(run=None):
    es = [e for e in _entries() if e.get("event") == "attack" and (run is None or e.get("run") == run)]
    if not es:
        return "no artifacts attacked yet"
    worst = max(es, key=lambda e: e["score"])
    lines = ["%d artifact(s) attacked, worst score %d — %s" % (len(es), worst["score"], worst["artifact"])]
    for e in sorted(es, key=lambda e: -e["score"])[:5]:
        lines.append("  %2d  %-44s %s" % (e["score"], e["artifact"][-44:], e["attacks"][0][:70]))
    return "\n".join(lines)


def main(argv):
    try:
        cmd = argv[1] if len(argv) > 1 else "summary"
        if cmd == "open":
            print(open_run(" ".join(argv[2:])))
        elif cmd == "record":
            print(record(argv[2], argv[3], int(argv[4]), argv[5:]))
        elif cmd == "max":
            print(max_score(argv[2]))
        elif cmd == "summary":
            print(summary(argv[2] if len(argv) > 2 else None))
        else:
            print(__doc__)
            return 2
        return 0
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 1
    except Corrupt as e:
        print("REFUSED (fail-closed): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
