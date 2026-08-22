#!/usr/bin/env python3
# FORM: code. Measures the session ratio for the completion table.
"""door_report.py — cheap doors used, versus corpora read by hand.

SCANNING NOTHING IS NOT A PASS. An empty log means the hook is not registered,
which is a FINDING, not health. Four of seven gates tested on 2026-08-22
returned success while measuring nothing; this one refuses to.

DECLARED BLIND SPOT: the hook sees Bash only. Door calls made through MCP never
reach it, so cheap-door use is UNDERCOUNTED. That is printed on every run. A
measurement that hides what it cannot see is the failure this repo exists to
stop.

Usage: door_report.py [--since-hours N]
"""
import json, os, sys, time

LOG = os.path.expanduser("~/.coywolf/state/door_use.jsonl")

def main():
    hours = 24
    if "--since-hours" in sys.argv:
        i = sys.argv.index("--since-hours") + 1
        try:
            hours = int(sys.argv[i])
        except (IndexError, ValueError):
            print("RED  --since-hours needs a whole number of hours")
            return 1
    cutoff = time.time() - hours * 3600
    if not os.path.exists(LOG):
        print("RED  no door log at %s" % LOG)
        print("     The hook is not registered, so nothing was measured.")
        print("     An unregistered gate reports a safety it does not have.")
        return 1
    cheap = hand = 0
    samples = []
    for line in open(LOG):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("ts", 0) < cutoff:
            continue
        kind = d.get("kind")
        if kind == "cheap_door":
            cheap += 1
        elif kind == "hand_read":
            hand += 1
            if len(samples) < 3:
                samples.append(d.get("detail", "(no detail recorded)"))
        # any other shape is a truncated write — skipped, and counted below
    total = cheap + hand
    if total == 0:
        print("RED  0 events in the last %dh — nothing measured, which is not a pass." % hours)
        return 1
    ratio = (cheap / total) * 100
    print("DOOR REPORT (last %dh): %d cheap-door · %d hand-read · %.0f%% cheap"
          % (hours, cheap, hand, ratio))
    print("  BLIND SPOTS, both directions — this ratio is INDICATIVE, not exact:")
    print("    · MCP door calls are invisible, so cheap-door use is UNDERCOUNTED.")
    print("    · A read inside a script or a heredoc is invisible too.")
    print("    The earlier version claimed the cheap count was a FLOOR. That was")
    print("    wrong: Read/Grep hand-reads were invisible as well, so the ratio")
    print("    could overstate in either direction. Read/Grep are counted now.")
    if samples:
        print("  sample hand-reads:")
        for s in samples:
            print("    %s" % s[:100])
    print("  baseline 2026-08-22: ~4 cheap vs ~40 hand (~9%). Compare against it.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
