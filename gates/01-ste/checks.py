#!/usr/bin/env python3
"""checks.py — the numbered conditions gate 01 enforces.

Each check has an id. Each id must have a bait in baits.py. `lint/baits_pair.py`
enforces that pairing. The rule is simple. A check is not done when it passes.
It is done when its bait has been seen to fail.

The pattern is copied from spirals/lint, which has a catch record. It is not
invented here. Three attempts at inventing one were refuted.

S1  an unreadable file is RED
S2  a file with no prose is RED
S3  ANY sentence over the hard limit is RED, whatever the median
S6  the GREEN line states only the proposition it checked
S7  a blockquoted list or table scores like an unquoted one
S4  a changeset with no markdown is N/A, never RED
S5  short clear prose is GREEN
"""
CHECKS = {
    "S1": "an unreadable file is RED",
    "S2": "a file with no prose is RED",
    "S3": "ANY sentence over the hard limit is RED, whatever the median",
    "S6": "the GREEN line states only the proposition it checked",
    "S7": "a blockquoted list or table scores like an unquoted one",
    "S4": "a changeset with no markdown is N/A, never a blocked commit",
    "S5": "short clear prose is GREEN",
}
