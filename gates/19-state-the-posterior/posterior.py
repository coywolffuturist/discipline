#!/usr/bin/env python3
"""posterior.py — gate 19's CALIBRATION form, and gate 18's reversibility dial.

Gate 19 has produced numbers for months and scored NONE of them. On 2026-09-07
one session asserted 0.93, 0.96, 0.97 and 0.99 and nothing anywhere recorded
whether any was right. A posterior that is never settled is a decoration with a
decimal point.

THE LOOP, adapted from bajpainaman/solve's calibration ledger (bin/calibration):
  log     a claim, its posterior, and WHICH DOOR it goes through
  settle  what actually happened
  audit   if HIGH claims are right less than 70% of the time over >=10 settled,
          RAISE the floor for that door. Being wrong costs you the right to
          assert cheaply.

THE DOOR IS GATE 18's DIAL (brick D). A reversible claim and a one-way door do
not deserve the same floor:
    reversible     -> SPEED   : floor 0.95
    one-way-door   -> QUALITY : floor 0.97, and gate 18 wants a refuter
The floors are not constants. The audit moves them, per door, from evidence.

SETTLEMENT IS THE WEAK POINT, and it is not hidden. A ledger nobody settles
reads 100% TBD forever. So: claims older than 30 days become `stale_no_followup`
and are EXCLUDED from the rate rather than counted as wins -- and if stale
outnumbers settled, `audit` REFUSES and says so, because a success rate computed
from the few claims someone bothered to close is not a success rate.

  posterior.py log <p> <door> <claim...>      door = reversible | one-way-door
  posterior.py settle <id> right|wrong [note]
  posterior.py floor [door]                   what may be asserted, per door
  posterior.py audit
  posterior.py stale
  posterior.py open
"""
import json, math, os, sys, time, uuid

STATE = os.path.expanduser(os.environ.get("POSTERIOR_STATE", "~/.claude/state"))
LEDGER = os.path.join(STATE, "posteriors.jsonl")
CFG = os.path.join(STATE, "posterior-config.json")
DOORS = ("reversible", "one-way-door")
DEFAULT_FLOORS = {"reversible": 0.95, "one-way-door": 0.97}
HIGH = 0.95
STALE_DAYS = 30
MIN_SETTLED = 10
DRIFT_RATE = 0.70
FLOOR_CAP = 0.99


class Corrupt(Exception):
    """FAIL CLOSED. A ledger that will not parse is never read as an empty ledger."""


def _floors():
    try:
        with open(CFG) as f:
            v = json.load(f)
    except FileNotFoundError:
        return dict(DEFAULT_FLOORS)
    except Exception as e:
        raise Corrupt("posterior-config.json unreadable: %s" % e)
    out = dict(DEFAULT_FLOORS)
    for d in DOORS:
        if d in v:
            f = v[d]
            if isinstance(f, bool) or not isinstance(f, (int, float)) or not math.isfinite(f) \
               or not 0 < f <= 1:
                raise Corrupt("floor for %s is not a probability: %r" % (d, f))
            out[d] = float(f)
    return out


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
            raise Corrupt("ledger line %d is not JSON: %s" % (n, ex))
        p = e.get("p")
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) \
           or not 0 <= p <= 1:
            raise Corrupt("ledger line %d has a non-probability p: %r" % (n, p))
        out.append(e)
    return out


def _write(entries):
    os.makedirs(STATE, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, sort_keys=True) + "\n")


def log(p, door, claim, adv=None):
    p = float(p)
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise SystemExit("REFUSED: p must be a probability in 0..1, got %r" % (p,))
    if door not in DOORS:
        raise SystemExit("REFUSED: door must be one of %s" % (DOORS,))
    claim = " ".join(claim).strip()
    if len(claim) < 10:
        raise SystemExit("REFUSED: name the claim — a number with no claim cannot be settled")
    if adv is not None:
        if isinstance(adv, bool) or not isinstance(adv, int) or not 0 <= adv <= 10:
            raise SystemExit("REFUSED: --adv must be an int 0..10 (adversary.py max <run>)")
    rec = {"id": uuid.uuid4().hex[:8], "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "p": p, "door": door, "claim": claim[:400], "outcome": "TBD",
           "session": os.environ.get("CLAUDE_SESSION_ID", "")[:8]}
    if adv is not None:
        rec["adv"] = adv
    os.makedirs(STATE, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    fl = _floors()[door]
    warn = "" if p >= fl else "  ⚠ BELOW the %s floor of %.2f — do not assert this as fact" % (door, fl)
    return "%s  p=%.2f %s%s" % (rec["id"], p, door, warn)


def settle(pid, outcome, note=""):
    if outcome not in ("right", "wrong"):
        raise SystemExit("REFUSED: outcome must be right or wrong")
    es = _entries()
    hit = [e for e in es if e.get("id") == pid]
    if not hit:
        raise SystemExit("REFUSED: no claim with id %s" % pid)
    hit[0]["outcome"] = outcome
    hit[0]["settled_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if note:
        hit[0]["note"] = note[:300]
    _write(es)
    return "%s settled %s" % (pid, outcome)


def mark_stale():
    es, now, n = _entries(), time.time(), 0
    for e in es:
        if e.get("outcome") != "TBD":
            continue
        try:
            age = now - time.mktime(time.strptime(e["ts"], "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            continue
        if age > STALE_DAYS * 86400:
            e["outcome"] = "stale_no_followup"
            n += 1
    if n:
        _write(es)
    return n


def audit():
    mark_stale()
    es = _entries()
    lines, changed = [], {}
    floors = _floors()
    for door in DOORS:
        d = [e for e in es if e.get("door") == door and e.get("p", 0) >= HIGH]
        settled = [e for e in d if e.get("outcome") in ("right", "wrong")]
        stale = [e for e in d if e.get("outcome") == "stale_no_followup"]
        openn = [e for e in d if e.get("outcome") == "TBD"]
        if len(stale) > len(settled):
            lines.append("%-13s REFUSED to score: %d stale vs %d settled. A rate computed from "
                         "the few claims someone closed is not a rate — settle them."
                         % (door, len(stale), len(settled)))
            continue
        if len(settled) < MIN_SETTLED:
            lines.append("%-13s not enough evidence: %d settled (need %d), %d open, %d stale"
                         % (door, len(settled), MIN_SETTLED, len(openn), len(stale)))
            continue
        right = sum(1 for e in settled if e["outcome"] == "right")
        rate = right / len(settled)
        lines.append("%-13s HIGH claims right %d/%d = %.0f%%  (floor %.2f)"
                     % (door, right, len(settled), rate * 100, floors[door]))
        if rate < DRIFT_RATE and floors[door] < FLOOR_CAP:
            new = min(round(floors[door] + 0.01, 2), FLOOR_CAP)
            changed[door] = (floors[door], new)
            floors[door] = new
            lines.append("%-13s CALIBRATION DRIFT: under %.0f%% — floor raised %.2f -> %.2f"
                         % (door, DRIFT_RATE * 100, *changed[door]))
    # THE WIRE (2026-09-07). His adversary scores and nothing reads it; this ledger
    # scores claims and never saw the adversary. Here they meet. The question is
    # falsifiable: if a high adversary score does NOT predict a claim that settles
    # wrong, gate 18's continuous form is theatre and gets cut on evidence.
    scored = [e for e in es if isinstance(e.get("adv"), int)
              and e.get("outcome") in ("right", "wrong")]
    hi = [e for e in scored if e["adv"] >= 7]
    lo = [e for e in scored if e["adv"] < 7]
    if len(hi) < MIN_SETTLED or len(lo) < MIN_SETTLED:
        lines.append("adversary signal: not enough evidence — %d settled claims scored >=7, "
                     "%d scored <7 (need %d each before the score means anything)"
                     % (len(hi), len(lo), MIN_SETTLED))
    else:
        rh = sum(1 for e in hi if e["outcome"] == "right") / len(hi)
        rl = sum(1 for e in lo if e["outcome"] == "right") / len(lo)
        lines.append("adversary signal: claims it scored >=7 settled right %.0f%% (%d), "
                     "claims it scored <7 settled right %.0f%% (%d)"
                     % (rh * 100, len(hi), rl * 100, len(lo)))
        lines.append("  %s" % ("the score PREDICTS — a high attack score earns weight"
                               if rl - rh >= 0.15 else
                               "the score predicts NOTHING here — gate 18's continuous form is "
                               "not paying for itself; cut it or change what it attacks"))
    if changed:
        os.makedirs(STATE, exist_ok=True)
        json.dump(floors, open(CFG, "w"), sort_keys=True)
    return "\n".join(lines) or "no HIGH claims logged yet"


def main(argv):
    try:
        cmd = argv[1] if len(argv) > 1 else "open"
        if cmd == "log":
            rest, adv = list(argv[4:]), None
            if "--adv" in rest:
                i = rest.index("--adv")
                adv = int(rest[i + 1])
                del rest[i:i + 2]
            print(log(argv[2], argv[3], rest, adv))
        elif cmd == "settle":
            print(settle(argv[2], argv[3], " ".join(argv[4:])))
        elif cmd == "floor":
            f = _floors()
            print(("%.2f" % f[argv[2]]) if len(argv) > 2 else
                  "  ".join("%s %.2f" % (d, f[d]) for d in DOORS))
        elif cmd == "audit":
            print(audit())
        elif cmd == "stale":
            print("%d claim(s) marked stale_no_followup" % mark_stale())
        elif cmd == "open":
            es = [e for e in _entries() if e.get("outcome") == "TBD"]
            print("%d unsettled claim(s)" % len(es))
            for e in es[-15:]:
                print("  %s  p=%.2f %-13s %s  %s" % (e["id"], e["p"], e["door"],
                                                     e["ts"][:10], e["claim"][:70]))
        else:
            print(__doc__)
            return 2
        return 0
    except Corrupt as e:
        print("REFUSED (fail-closed): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
