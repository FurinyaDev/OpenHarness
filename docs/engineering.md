# Engineering guide

Start with the [minimal entry](../README.md#minimal-core-for-a-new-project).
Use this guide when the task needs an engineering decision or a guardrail.
The project owns architecture, thresholds, commands, CI, and release policy.
Track scope, dependencies, progress, and acceptance in its existing Issues or
Backlog. Git and the hosting platform provide current head, base, and delivery
state. Keep platform evidence with the actual candidate.

## Intent and architecture

Use [REASONS](templates/reasons.md) for new domains, important contracts, complex
features, or major refactors. For a small fix, use the existing task scope and
acceptance criteria. Update intent and acceptance before changing behavior.
For structural refactors, preserve the confirmed behavior and update affected
structure documentation with the change. Confirm unexpected existing behavior
with the task owner before adopting it as a requirement.

Use the project's decision location for major architectural decisions. The
[short ADR](templates/adr.md) covers one decision and its trade-offs. Preserve
superseded decisions and link their successors.

- Give each authoritative business state a clear owner and write entry point.
  Specify how caches, projections, and UI copies stay current. UI can own focus,
  input, and animation state.
- Keep core business rules and state owners independent of UI, rendering,
  databases, and platform SDKs. Use explicit ports for infrastructure and wire
  implementations at the composition root. Exercise core behavior headlessly
  with controlled time, randomness, and storage. Use integration tests for real
  infrastructure, engines, or devices where required.
- Depend on public contracts across domains. Declare allowed direction and keep
  shared code neutral. Domain-first directories can help when they express real
  boundaries. Add events where delivery, ordering, and state ownership are clear.
- To migrate incrementally, record current behavior and the intended boundary,
  find a seam, add a thin adapter if needed, replace and verify one capability
  at a time, then remove the old path when its stated exit condition is met.

## Guardrails and evidence

Enable a guardrail through the project's actual tool and existing CI when its
input and scope are reliable. Record the policy source, command, tool version,
coverage, missing capability, and representative pass and fail. Enabled but
unavailable tools, bad inputs, or parse failures leave the check incomplete or
failed. The [recipes](engineering-recipes.md) include executable examples.

| Check | Project policy and tool responsibility | Reviewer responsibility |
| --- | --- | --- |
| Dependency direction and cycles | Declare boundaries and resolve real imports, including analyzable delayed imports. For an SCC ratchet, check membership and internal edges as well as newly formed cycles. | Verify public contracts, state ownership and the treatment of runtime loading or unsupported imports. |
| Complexity and file size | Specify source scope, physical/logical lines, function identity and counting convention. Apply incremental limits to new and changed code where history requires a ratchet. Preserve rename, move and generated-file handling. | Check that the threshold, historical matches, exclusions and changes reflect the intended policy. |
| PR size | Declare the comparison, line and file metrics, and handling of binary files and moves. Report overall and production scope according to project policy. | Prefer independently deliverable slices. Review each project-native exception against an objective reason and reproducible evidence. |
| Behavior and delivery | Run relevant tests, native CI and additional acceptance according to project policy. | Check test expectations and manual or device evidence against the task and exact candidate. |

Project limits and exception processes take precedence. Start with the
existing checker and its regression tests. Demonstrate a newly configured
guardrail's clean case and a real violation in an isolated fixture or repo.
A setup error only tests incomplete execution. Record actual wall time and use
the project's appropriate check tier. Keep tasks, CI routing and merge gates in
the existing tools.

## Test contracts

Use suitable combinations of data scenarios, confirmed behavior traces,
property or invariant tests, and normal unit, integration, and device tests.
Ground expectations in requirements, domain knowledge, an independent reference
or approved examples. Treat implementation-derived output as characterization
until confirmed. A matching golden reports agreement for the covered cases.
For a behavior change, link the requirement behind any new expectations.
Retain assertions, coverage, and filters unless the underlying contract calls
for a reviewed change. Keep failures reproducible with controlled seeds, time,
and inputs. Choose repetitions by risk and cost. Account for creation,
consumption and deletion when deriving invariants.

## Independent review and handoff

Put these fields in the existing PR or review process for the change.

- Task or REASONS, scope, expected behavior, and affected contracts.
- Exact reviewed head, base, and result tree where the project uses one.
- State owners, dependency boundaries, exception rationale, and risks.
- Commands, fresh results, test expectation sources, any required manual or
  device evidence, and checks or acceptance still pending.
- Independent reviewer/context, findings, disposition, and unresolved items.

Use a genuinely separate review context. Recheck the affected review and
verification when its subject changes. Report local checks, hosted checks,
actual integration, and applicable acceptance with their own evidence.
Follow the repository's existing native approval and delivery flow.

## Sources

The seven REASONS sections are from Wei Zhang and Jessie Jie Xia's
[Structured-Prompt-Driven Development](https://martinfowler.com/articles/structured-prompt-driven/).
This guide's planning fields and adoption recipes are local implementation choices.

- Advance guidance, feedback, executable checks, and semantic judgment.
  [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)
- Readable behavioral scenarios and separation of data from execution.
  [Tests as data](https://martinfowler.com/articles/tests-as-data.html)
- Incremental replacement and temporary architecture.
  [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)
- Decision records and trade-offs.
  [Architectural Decision Records](https://adr.github.io/)
- Concise context, verification feedback, and deterministic hooks.
  [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
