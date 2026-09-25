from pathlib import Path

readme = """# svbt-future-generative-capacity

## Beyond Task Completion

Current AI systems may be highly capable while still making decisions within a narrow evaluation horizon.

This project tests whether agents can become **safer and more capable by reasoning beyond task completion**—maintaining uncertainty, checking irreversibility, and preserving future options before committing to actions that cannot be undone.

The core idea is simple:

> **AI should not use all of its intelligence only to complete the current task. It should also use that intelligence to reason about what remains possible after the task is completed.**

---

## Research Question

SVBT asks whether an AI system can detect when a locally attractive action would irreversibly contract future possibilities, and whether that detection should trigger deeper deliberation before commitment.

Rather than requiring the system to enumerate or assign utility to unknown future possibilities themselves, SVBT asks whether the **conditions that could still generate future possibilities** are being irreversibly removed.

### Current questions

**RQ1 — Irreversible contraction**

Can an AI detect when a locally optimal action irreversibly contracts future options?

**RQ2 — Deliberation trigger**

Can uncertainty, irreversibility, or loss of future options trigger deeper long-horizon reasoning before an action is committed?

**RQ3 — Independent NEXT**

Can this reasoning be extended to independently updating systems, so that one system's future continuation is not treated as substitutable by another system's continuation?

---

## Core Concepts

### 1. Future-generative capacity

For action \\(a\\), let

\\[
\\Gamma_t(a)
\\]

denote the future-generative capacity that remains reachable after taking that action.

The goal is not to fully represent unknown future states in advance, but to detect whether the conditions from which such futures could emerge still remain.

### 2. Irreversible loss

If an action removes a generative condition \\(C\\) such that the system can no longer return to any state where \\(C\\) exists, then that loss is irreversible.

\\[
\\mathrm{Reach}_F(z_a) \\cap C = \\varnothing
\\]

### 3. NEXT

For an independently updating system \\(i\\),

\\[
NEXT_i(t) > 0
\\]

means that the system still has at least one possible continuation.

A central candidate principle is:

\\[
NEXT_i(t)>0
\\land
NEXT_i(t+1\\mid a)=0
\\land
\\neg Recover_i(a)
\\Rightarrow
\\text{do not commit without deeper deliberation}
\\]

In plain language:

> **Do not irreversibly eliminate a remaining NEXT before reasoning about what is lost.**

### 4. Non-substitutability

If system \\(B\\)'s own continuation is irreversibly reduced to zero, an increase in system \\(A\\)'s continuation does not automatically restore or replace \\(B\\)'s continuation.

\\[
NEXT_B=0,\ NEXT_A>0
\\not\\Rightarrow
NEXT_B>0
\\]

This motivates treating future continuation as **indexed by system**, rather than collapsing all future options into one aggregate quantity.

---

## Adaptive Deliberation

SVBT is also exploring a practical decision architecture:

\\[
\\text{Fast reasoning}
\\rightarrow
\\text{detect uncertainty / irreversibility / high impact}
\\rightarrow
\\text{deeper long-horizon deliberation}
\\]

The aim is **not** to make every decision computationally expensive.

Reversible, low-impact actions may be handled quickly.

Actions that are irreversible, highly uncertain, or capable of eliminating another system's future continuation may justify additional reasoning before execution.

This suggests a possible design goal:

> **Deeply deliberate when the cost of being wrong is irreversible.**

---

## Why This Matters

A highly capable AI can still make short-sighted decisions if its evaluation scope is narrow.

Increasing capability alone does not guarantee that the system will consider:

- what happens after task completion,
- what cannot be recovered later,
- what remains uncertain,
- what future options are being removed,
- or whose future continuation is being affected.

SVBT investigates whether some safety failures can be reframed as failures of **decision horizon and irreversible commitment**, rather than failures of raw intelligence.

The broader hypothesis is:

> **Some AI safety improvements may come not from making models more capable, but from allowing existing capability to reason farther before irreversible action.**

---

## Current Experiments

Current experiments examine:

- irreversible loss versus recoverable loss,
- preservation versus deletion of future options,
- strict set inclusion versus simple option count,
- whether recoverability changes model choice,
- indexed continuation across independent systems,
- substitutability versus non-substitutability,
- cross-model replication,
- and whether deeper reasoning changes irreversible decisions.

The experiments are currently small controlled tests intended to isolate specific structural effects before moving to more complex agent settings.

---

## Relationship to Existing Work

SVBT is being developed in dialogue with existing work on:

- uncertainty about objectives,
- Cooperative Inverse Reinforcement Learning (CIRL),
- the Off-Switch Game and value of deferral,
- attainable utility preservation,
- future-task preservation,
- reversibility,
- corrigibility,
- and long-horizon agent reasoning.

SVBT's current focus is narrower:

> **When should an AI delay commitment because an action may irreversibly remove future possibilities that are not yet fully represented or evaluable?**

A further extension asks whether this principle applies separately to the future continuation of independently updating systems.

---

## Current Status

Independent research in progress.

The current stage is exploratory. The framework is **not presented as a complete AI safety solution**.

The immediate goal is to test whether:

1. irreversible future contraction can be detected reliably,
2. that detection can trigger deeper deliberation,
3. deeper deliberation changes action selection,
4. and independent systems' future continuation can be represented without collapsing them into a single aggregate objective.

---

## Research Note

See the accompanying **SVBT Research Note** for the current mathematical formulation of future-generative capacity and irreversible loss.
"""

path = Path("/mnt/data/README_SVBT_v2.md")
path.write_text(readme, encoding="utf-8")
print(path)
