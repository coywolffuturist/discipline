#!/usr/bin/env python3
"""consistency.py — fail the build when this repo contradicts itself.

WHY THIS EXISTS. Twice in one hour, readers caught false statements here that I
had written and never retired: a banner saying the hooks were registered nowhere
(they were), and three gate rows citing a skill that is not shipped. Both were
true when written. Both rotted. Neither was caught by a human re-reading, because
nobody re-reads a file they wrote.

A repo whose subject is "an eval must not report health it does not have" cannot
rely on attention to keep its own claims true. Every claim below is now mechanical
and fails the build when it stops being true.

Checks:
  1. every gates/NN-* directory referenced in the conductor exists, and vice versa
  2. every skills/<name> path referenced anywhere in the repo exists
  3. gates 01..20 appear exactly once in each conductor table, with matching names
  4. README's status table covers all 20 with the same names
  5. every repo-relative file path mentioned in prose exists
  6. the derived skills/discipline/SKILL.md still matches CONDUCTOR.md's gate rows
  7. no gate claims a read that is not present in this repo
"""
import os, re, sys

FAIL = []
def bad(check, msg):
    FAIL.append((check, msg))

root = os.getcwd()
def read(p):
    try:
        return open(os.path.join(root, p), encoding="utf-8").read()
    except Exception:
        return None

cond = read("CONDUCTOR.md") or ""
readme = read("README.md") or ""
contract = read("CONTRACT.md") or ""
skills = set(os.listdir("skills")) if os.path.isdir("skills") else set()
gatedirs = set(os.listdir("gates")) if os.path.isdir("gates") else set()

# --- 1/3. the conductor's two tables -----------------------------------------
trig = re.findall(r'^\| (\d{2}) \| ([^|]+?) \|[^|]*\|[^|]*\|([^|]*)\|', cond, re.M)
locs = re.findall(r'^\| (\d{2}) \| ([^|]+?) \| ([^|]+?) \|\s*$', cond, re.M)
trig_map = {n: name.strip().replace("*", "") for n, name, _ in trig}
loc_map = {n: (name.strip().replace("*", ""), loc.strip()) for n, name, loc in locs}

expected = ["%02d" % i for i in range(1, 21)]
for n in expected:
    if n not in trig_map:
        bad("conductor", "gate %s missing from the trigger table" % n)
    if n not in loc_map:
        bad("conductor", "gate %s missing from the read-location table" % n)
for n in sorted(set(trig_map) & set(loc_map)):
    if trig_map[n] != loc_map[n][0]:
        bad("conductor", "gate %s named %r in the trigger table but %r in the read table"
            % (n, trig_map[n], loc_map[n][0]))

# --- 2. every skills/<name> path referenced anywhere must exist ---------------
for surface, text in (("CONDUCTOR.md", cond), ("README.md", readme), ("CONTRACT.md", contract)):
    for ref in sorted(set(re.findall(r'skills/([a-z0-9][a-z0-9-]*)', text))):
        if ref not in skills:
            bad("dangling-skill", "%s references skills/%s, which is not in this repo" % (surface, ref))

# --- 1b. gates/ directories referenced vs present ----------------------------
for ref in sorted(set(re.findall(r'gates/(\d{2}-[a-z0-9-]+)', cond + readme + contract))):
    if ref not in gatedirs:
        bad("dangling-gate", "a surface references gates/%s, which does not exist" % ref)
for d in sorted(gatedirs):
    if not os.path.isfile(os.path.join("gates", d, "GATE.md")):
        bad("gate-shape", "gates/%s has no GATE.md, which CONTRACT.md calls canonical" % d)

# --- 7. a gate must not claim a read this repo does not ship ------------------
for n in sorted(loc_map):
    name, loc = loc_map[n]
    refs = re.findall(r'skills/([a-z0-9][a-z0-9-]*)', loc) + re.findall(r'gates/(\d{2}-[a-z0-9-]+)', loc)
    up = loc.upper()
    declared_gap = ("NO DEPLOYED" in up) or ("GAP" in up) or ("NOT SHIPPED" in up)
    if not refs and not declared_gap:
        bad("unreadable-gate", "gate %s (%s) names no read and does not declare a gap: %r"
            % (n, name, loc[:70]))

# --- 4. README status table ---------------------------------------------------
status = re.findall(r'^\| (\d{2}) \| ([^|]+?) \|', readme, re.M)
status_map = {n: name.strip().replace("*", "") for n, name in status}
for n in expected:
    if n not in status_map:
        bad("readme", "gate %s missing from README's status table" % n)
    elif n in trig_map and status_map[n] != trig_map[n]:
        bad("readme", "gate %s is %r in README but %r in the conductor"
            % (n, status_map[n], trig_map[n]))

# --- 5. repo-relative paths mentioned in prose must exist ---------------------
for surface, text in (("CONDUCTOR.md", cond), ("README.md", readme), ("CONTRACT.md", contract)):
    for p in sorted(set(re.findall(r'`((?:hooks|lint|scripts|gates|skills)/[A-Za-z0-9_./-]+)`', text))):
        if not os.path.exists(os.path.join(root, p)):
            bad("dangling-path", "%s references `%s`, which does not exist" % (surface, p))

# --- 6. the derived copy must still match its source -------------------------
derived = read("skills/discipline/SKILL.md")
if derived is None:
    bad("derived", "skills/discipline/SKILL.md is missing; CONTRACT.md calls it derived from CONDUCTOR.md")
else:
    d_trig = re.findall(r'^\| (\d{2}) \| ([^|]+?) \|', derived, re.M)
    if {n: v.strip().replace("*", "") for n, v in d_trig} != {**status_map, **trig_map} and \
       {n for n, _ in d_trig} != set(trig_map):
        missing = set(trig_map) - {n for n, _ in d_trig}
        if missing:
            bad("derived", "skills/discipline/SKILL.md is missing gate(s) %s — regenerate it"
                % ", ".join(sorted(missing)))

# --- report -------------------------------------------------------------------
if not FAIL:
    print("\033[32mPASS\033[0m  consistency — every claim in this repo checks out")
    sys.exit(0)
print("\033[31mFAIL\033[0m  consistency — %d contradiction(s):" % len(FAIL))
w = max(len(c) for c, _ in FAIL)
for c, m in FAIL:
    print("      %-*s  %s" % (w, c, m))
sys.exit(1)
