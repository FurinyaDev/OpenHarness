# REASONS — [change]

Record this in the existing task or link it from there. Use the full canvas for
new domains, important contract changes, complex features, or major refactors.
For a small fix, use the task's scope and acceptance criteria.

## R — Requirements

- Problem and observable result.
- Scope In / Out.
- Acceptance checks in Given / When / Then form.

## E — Entities

- Entities and relationships.
- Authoritative state owners, write entry points, and key invariants.
- How derived values, caches, or presentation copies stay current.

## A — Approach

- Implementation strategy, alternatives, why this one fits, and capabilities
  deliberately left out.

## S — Structure

- Actual file locations, public contracts, allowed and prohibited dependencies.
  Use signatures from existing code or mark them as proposed contracts.

## O — Operations

- Usually three to six dependency-ordered steps. Name the actual interfaces,
  method responsibilities, and verification point for each step.

## N — Norms

- Link project naming, error-handling, logging, test, PR, and delivery guidance.

## S — Safeguards

- Performance and resource boundaries, security constraints, prohibited
  behavior, and the relevant executable check or manual acceptance.
