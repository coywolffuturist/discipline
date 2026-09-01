---
name: adversarial-inverse
description: Mandatory audit BEFORE locking ANY mechanism participants interact with for value — tokenomics, market/auction design, smart contracts, fee/incentive structures, treasuries, slashing, governance, eligibility/distribution rules, tokenized-asset issuance/redemption/settlement. Construct the adversarial inverse — how could a participant, counterparty, coalition, or outside attacker exploit this for +EV harm? — and either close every exploit OR name the unclosed trade-offs explicitly, BEFORE locking. Shorthand "adinv" / "audit the inverse".
---

# Adversarial Inverse Audit

**No value-bearing mechanism is complete until its adversarial inverse
is named.** A mechanism that "works when used as intended" is
half-designed. The other half is "withstands deliberate misuse." Both
must be explicit BEFORE locking. Domain-agnostic: a DAO treasury, an
auction, and a tokenized energy off-take agreement all qualify.

## When this fires (red flags requiring the audit)

- REDISTRIBUTES value on a triggered event (slashing, forfeiture, fee,
  fine, penalty, liquidation).
- AUTOMATIC or UNBOUNDED allocation, minting, or emission.
- Creates obligation/duty in response to external action (response
  protocols, claims, guarantees, off-take or redemption commitments).
- One party's loss → another party's gain.
- Depends on a PRICE, ORACLE, or external data feed that can be moved.
- Involves SETTLEMENT, COLLATERAL, or LEVERAGE mechanics.
- Promises pursuit / enforcement against external actors.
- Any threshold or eligibility gate reverse-engineerable to game.

> These lists name common vectors, not all of them. The exploit that
> actually breaks you is often native to THIS mechanism's own sector
> and appears on no general list — name those sector-specific vectors
> explicitly before locking.

## The 5-step audit (mandatory pre-proposal)

### 1. Who benefits from abuse?

Every party who could extract value by manipulating the mechanism:
participants, counterparties, outside attackers, coalitions/cartels,
sybil swarms, oracle/data manipulators, insiders/operators,
judgment-proof actors — plus any role specific to this sector.

### 2. What is the exploit math?

For each abuser: `cost-to-attacker / damage-to-system /
extraction-value`. If any path is **net-positive for the adversary**,
the mechanism is broken.

### 3. What is the worst-case extraction?

Treat the mechanism as a primitive in an attacker's toolkit:
> "If I wanted to drain / corner / capture / dominate, would this give
> me leverage?"

### 4. What is the coordination vector?

Could a coalition or cartel amplify it? Sybils? Wash trading? A
flash-funded attack? External + internal collusion? A vector unique to
this sector's structure?

### 5. What bound closes it?

Choose from: hard caps, circuit breakers, proportionality limits,
over-collateralization, oracle redundancy / TWAP / settlement delay,
time locks, dispute/arbitration gating, bounty-preferred-over-direct-
spend, escalation premiums, splitting immediate-operational from
delayed-financial consequences — or a bound the sector itself supplies.

## The design principle

```
NO MECHANISM IS COMPLETE UNTIL ITS ADVERSARIAL INVERSE IS NAMED.

A mechanism that "works when used as intended" is half-designed.
The other half is "withstands deliberate misuse."
Both must be explicit in the design before locking.
```

**The audit IS the design work.** Mechanisms that survive a serious
adversarial audit are rare; most break under examination. Skipping it
ships approximately worthless designs — and the cost is asymmetric: a
human reviewer can't catch everything, so a missed exploit ships.

For high-stakes mechanisms (real capital, irreversible settlement),
spawn the `mechanism-auditor` agent to run this audit independently —
a fresh adversarial context that didn't design the thing.
