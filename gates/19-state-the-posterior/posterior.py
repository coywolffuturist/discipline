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
                                              a HIGH claim needs an ANCHOR:
                                              a sha, path, page name or filename
                                              (--no-anchor to override, with reason)
  posterior.py settle <id> right|wrong [note]
  posterior.py floor [door]                   what may be asserted, per door
  posterior.py audit                          read-only: what the floor WOULD do
  posterior.py audit --apply                  the only form that moves the floor
  posterior.py stale
  posterior.py open
"""
import json, math, os, re, sys, time, uuid

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
# Above this, calibration has recovered and the floor should come back DOWN.
# The gap between DRIFT_RATE and RECOVER_RATE is deliberate hysteresis: without
# it a rate oscillating around one threshold would move the floor every audit.
RECOVER_RATE = 0.80
# Key in the config recording how many settled claims justified the last move,
# per door. A move requires MORE settled claims than last time. This is what
# makes audit idempotent: the same evidence cannot be charged twice, and a
# second agent running audit does not double-charge it either.
MARK_KEY = "_settled_at_last_move"
# An ANCHOR is anything a future reader can go and check: a commit sha, a path,
# or a canon page name. MEASURED 2026-09-21 over 237 logged claims: a claim
# carrying a page name settled 100% of the time, a sha 81%, a bare path 56%,
# and a claim with only a number 39%. Of 122 claims still open, 100 carried NO
# anchor at all -- not a backlog problem but a WRITER problem, because a claim
# with nothing to check is unsettleable the moment its author forgets the
# context, which is about an hour.
ANCHOR_RE = re.compile(
    r"\b[0-9a-f]{7,40}\b"                                        # commit sha
    r"|(?:^|\s)[~/][\w./-]{3,}"                                   # a path
    r"|\b(?:feedback|decision|incident|correction|reference|project)_[a-z0-9_]{4,}"  # canon page
    r"|\b[\w./-]+\.(?:py|sh|md|json|ya?ml|txt|plist)\b"          # a named file
)


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


def log(p, door, claim, adv=None, no_anchor=False):
    p = float(p)
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise SystemExit("REFUSED: p must be a probability in 0..1, got %r" % (p,))
    if door not in DOORS:
        raise SystemExit("REFUSED: door must be one of %s" % (DOORS,))
    claim = " ".join(claim).strip()
    if len(claim) < 10:
        raise SystemExit("REFUSED: name the claim — a number with no claim cannot be settled")
    # The same rule, one rung up. A claim with no ANCHOR cannot be settled
    # either: nobody can find what it refers to, including its author later.
    # Only HIGH claims are gated, because those are the ones that move the
    # floor -- a low-confidence note costs nothing if it goes unsettled.
    anchored = bool(ANCHOR_RE.search(claim))
    if p >= HIGH and not anchored and not no_anchor:
        raise SystemExit(
            "REFUSED: a HIGH claim needs an ANCHOR — a commit sha, a path, a canon page\n"
            "  name or a filename. Without one nobody can settle it, including you in an\n"
            "  hour. Measured: anchored HIGH claims settle 81-100%, unanchored ones 39%,\n"
            "  and 100 of 122 open claims carry no anchor at all.\n"
            "  Add the artifact, or pass --no-anchor if the claim is genuinely about an\n"
            "  observation with no artifact (a delivery, a runtime behaviour).")
    if adv is not None:
        if isinstance(adv, bool) or not isinstance(adv, int) or not 0 <= adv <= 10:
            raise SystemExit("REFUSED: --adv must be an int 0..10 (adversary.py max <run>)")
    rec = {"anchored": anchored,
           "id": uuid.uuid4().hex[:8], "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
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


def audit(apply=False):
    """Read-only by default. Only `apply=True` writes the floor.

    An audit must never write: the previous version mutated global
    state on every invocation, so looking at the calibration changed it.
    """
    mark_stale()
    es = _entries()
    lines, changed = [], {}
    floors = _floors()
    try:
        marks = dict(json.load(open(CFG)).get(MARK_KEY, {}))
    except Exception:
        marks = {}
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
        # IDEMPOTENCE. Move only when THIS evidence is new. Without the mark,
        # audit raised +0.01 per invocation: 0.95 -> 0.99 in one session on an
        # unchanged 7/11, four raises from four glances.
        seen = int(marks.get(door, 0))
        fresh = len(settled) > seen

        if rate < DRIFT_RATE and floors[door] < FLOOR_CAP:
            if fresh:
                new = min(round(floors[door] + 0.01, 2), FLOOR_CAP)
                changed[door] = (floors[door], new)
                floors[door] = new
                marks[door] = len(settled)
                lines.append("%-13s CALIBRATION DRIFT: under %.0f%% — floor %s %.2f -> %.2f"
                             % (door, DRIFT_RATE * 100,
                                "raised" if apply else "WOULD RISE", *changed[door]))
            else:
                lines.append("%-13s under %.0f%%, but this evidence already moved the floor "
                             "(%d settled at last move) — no change"
                             % (door, DRIFT_RATE * 100, seen))
        elif rate >= RECOVER_RATE and floors[door] > DEFAULT_FLOORS[door]:
            # DECAY. A penalty with no route back stops being an incentive and
            # becomes a tax. Never below the default.
            if fresh:
                new = max(round(floors[door] - 0.01, 2), DEFAULT_FLOORS[door])
                changed[door] = (floors[door], new)
                floors[door] = new
                marks[door] = len(settled)
                lines.append("%-13s RECOVERED: %.0f%% >= %.0f%% — floor %s %.2f -> %.2f"
                             % (door, rate * 100, RECOVER_RATE * 100,
                                "lowered" if apply else "WOULD FALL", *changed[door]))
            else:
                lines.append("%-13s recovered, but this evidence already moved the floor "
                             "(%d settled at last move) — no change"
                             % (door, seen))
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
    if changed and apply:
        os.makedirs(STATE, exist_ok=True)
        payload = dict(floors)
        payload[MARK_KEY] = marks
        json.dump(payload, open(CFG, "w"), sort_keys=True)
    elif changed:
        lines.append("DRY RUN — nothing written. Re-run `posterior.py audit --apply` "
                     "to move the floor. This split exists because audit used to "
                     "mutate the floor every time it was consulted.")
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
            # The escape hatch is a FLAG, not a silent default: a claim with no
            # artifact is legitimate (a delivery, a runtime behaviour), but the
            # author has to say so rather than drift into it.
            no_anchor = "--no-anchor" in rest
            if no_anchor:
                rest.remove("--no-anchor")
            print(log(argv[2], argv[3], rest, adv, no_anchor))
        elif cmd == "settle":
            print(settle(argv[2], argv[3], " ".join(argv[4:])))
        elif cmd == "floor":
            f = _floors()
            print(("%.2f" % f[argv[2]]) if len(argv) > 2 else
                  "  ".join("%s %.2f" % (d, f[d]) for d in DOORS))
        elif cmd == "audit":
            print(audit(apply=("--apply" in argv)))
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
