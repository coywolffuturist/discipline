---
name: vizcheck
description: Hard rule — anything visual must be verified as having achieved its intent AFTER being pushed to its intended (rendered/deployed) form, never from code that should produce it. Render the real surface, read the pixels, and escalate to crop + coordinate readback when placement must be exact. Syntax checks (`node --check`), curl, and reviewing your own code do NOT substitute — DOM-correct can still be visually wrong. The user is never the QA tester. Shorthand "vizcheck" / "chromeqa" (legacy).
---

# Vizcheck — verify the intent in the rendered form

**Anything visual must be verified as having achieved its intent after
being pushed to its intended form.**

Two load-bearing words: *intent* (does the rendered result match what
was wanted — not merely "did the code change land") and *pushed to its
intended form* (verify the artifact in the state the user will see it —
deployed, built, refreshed — not a local pre-build proxy). Code that
*should* render correctly is a hypothesis; the rendered pixels are the
evidence.

## When this fires

Any change touching HTML / CSS / JS; dashboard or app surfaces; dialog
positioning; modal / drawer / rail / sidebar layout; z-index, overflow,
padding, margin, scroll — anything a human would visually evaluate.

## The verification — scale it to how exact the intent is

A multimodal model genuinely sees rendered pixels (a screenshot read
into context is evaluated as the bitmap, not the code). But vision is
*perceptual, not metric* — it reads layout, overlap, clipping, legibility,
colour; it does NOT read exact offsets or 1–2px differences. So match the
rung to the intent:

1. **Render & look** (gross intent: "centered, in the rail, nothing
   overlaps or clips"). Push to its rendered form, screenshot it, read
   the pixels. Confirms placement, overlap, overflow, z-order, legibility.
2. **Crop / zoom** small targets so their pixels are large enough to
   read accurately — don't judge 11px text from a full-page shot.
3. **Coordinate readback** when the intent is *exact* ("24px gutter,
   aligned to the grid"): pull `getBoundingClientRect()` / computed style
   from the live surface. The screenshot proves it *looks* right; the
   readout proves it *is* at the intended position. Together = metric-grade.
4. **Baseline diff** for regressions: compare against a known-good
   screenshot rather than eyeballing "looks the same."

The intent itself sets the rung. Don't claim exact placement from a
perceptual glance; don't burn a coordinate readback when "it's in the
right region" was the whole spec.

## If verification fails

Run the environment's screenshot DIAGNOSTIC first — never blame
permissions, TCC, or a remembered past incident before the diagnostic
names the current failure (see `root-cause`). If the QA stack reports
healthy and the shot still looks wrong, the bug is in the page.

## Don't

- ❌ "Refresh and try it" / "this should work now" without rendering.
- ❌ Substitute `node --check` or `curl` for visual confirmation.
- ❌ "The HTML looks right" — DOM-correct can still be visually wrong.
- ❌ Claim exact placement from a perceptual screenshot alone.
- ❌ Patch blindly, then ask the user to check — wastes their turns.

## One-line summary

**Push it to its rendered form, then prove it achieved its intent —
pixels for what it looks like, coordinates for where it sits. Never
ship code that *should* look right.**
