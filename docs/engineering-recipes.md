# Guardrail recipes

Use the [guide](engineering.md) to choose the checks a project needs. Keep
existing working commands, configs, CI and exception rules. Copy examples from
the same reviewed OpenHarness commit used for the [entry](../README.md#minimal-core-for-a-new-project).
Merge settings into existing project configs through review.

## JavaScript dependency and quality checks

This example applies to Node 24 ESM JavaScript (`.js` and `.mjs`) in `src/`. The example limits
are deliberately small for a fixture. Adopt the project's own limits and
boundaries. Use the existing lockfile and package manager where possible.

```sh
npm install --save-dev --save-exact dependency-cruiser@18.8.0 eslint@10.15.0
```

Adapt [dependency-cruiser.cjs](examples/dependency-cruiser.cjs) and
[eslint.config.mjs](examples/eslint.config.mjs). Add the following commands to
the project's existing package scripts and call them from its normal check tier.

```json
{
  "check:deps": "npm run check:quality && depcruise --config dependency-cruiser.cjs src",
  "check:quality": "eslint --no-ignore 'src/**/*.{js,mjs,cjs,jsx}' --max-warnings 0"
}
```

In a temporary ESM package, create `src/core/value.js` with
`export const value = 1;` and `src/ui/view.js` with
`import { value } from "../core/value.js"; export const view = value;`.
Both commands should exit zero. Exercise these separate violations.

| Fixture change | Expected rejection |
| --- | --- |
| Add a literal `import("../ui/view.js")` in a core function | dependency-cruiser names `core-to-ui` and the new source cycle |
| Import a nonexistent local file | dependency-cruiser reports an unresolved dependency |
| Add a function with three consecutive `if` statements | ESLint reports CC 4 against the example max 3 |
| Add enough comments to reach 13 lines | ESLint reports `max-lines` |
| Replace a literal dynamic import with `import(name)` or `import(7)` | ESLint requires a string literal |
| Add invalid JavaScript or omit installed dependencies | Parser or executable errors leave the applicable checks failed |

The dependency command runs ESLint first so a parse failure or computed import
stops the gate before graph construction. The graph includes analyzable module
edges such as literal dynamic imports. The example uses direct source ESM,
without CommonJS-specific checks, JSX, TypeScript, bundler aliases, generated
modules, or runtime loaders. Projects using those features need separately
validated resolution and coverage. ESLint counts physical source lines
including comments and blank lines, and applies its standard cyclomatic
complexity rule per function or other defined code path. This example uses
absolute limits. A project with historical debt needs its own incremental
policy, such as the Lua reference below.

## PR size

Use the project's own size checker first. If all paths share one budget,
[check_pr_size.py](examples/check_pr_size.py) adapts native Git numstat. Copy
it to a project-owned tools path and call it in the existing PR check after
checking out or fetching both reviewed commits.

```sh
python tools/check_pr_size.py "$BASE_SHA" "$HEAD_SHA" --max-lines 20 --max-files 3
```

The commits are explicit. Use the comparison your CI declares, such as PR
merge-base to head or target base to merged candidate. The example prints all-path
file totals and textual additions plus deletions. It counts moves as delete
plus add and fails changes that Git classifies as binary under its diff rules
and attributes. All paths count toward the illustrative
budget. Projects that classify production, test or generated files or allow
exceptions should use a checker that implements and reports those policies.
Keep the overall totals visible alongside any narrower gate.

In a temporary repo, compare a one-line commit with its parent for a pass.
Compare a 21-line addition under the same settings for a policy failure.
Add a binary in a separate candidate for a binary failure. A missing reviewed
commit produces an incomplete check. Compare the output and exit code.

## Connect existing tools

For a project already using OpenHarness candidate verification, its
[existing configuration](../README.md#optional-strict-bootstrap) accepts
argv in `verification.commands`:

```json
{
  "commands": [
    ["npm", "run", "check:deps"]
  ]
}
```

Preserve existing commands and review additions through the project's
configuration process. Candidate verification runs on a clean merged-result
checkout. Provide pinned dependencies in the project's approved environment
or [offline build image](offline-dependencies.md). PR size needs the original
comparison commits and the project PR context. Keep that check in the
existing PR workflow unless its candidate runner already provides those
inputs. Supported runtime modes and prerequisites are in the
[cooperative workflow](cooperative-workflow.md) and the frozen contract.

For a Lua project with existing guardrails, see the pinned Slay-the-Heavens
[architecture policy](https://github.com/FurinyaWorks/Slay-the-Heavens/blob/b836c54361eece5bd9f6860487268e3cf7e8ff83/config/architecture.json),
[quality ratchet](https://github.com/FurinyaWorks/Slay-the-Heavens/blob/b836c54361eece5bd9f6860487268e3cf7e8ff83/scripts/check-quality-ratchet.mjs),
and [PR sizing policy](https://github.com/FurinyaWorks/Slay-the-Heavens/blob/b836c54361eece5bd9f6860487268e3cf7e8ff83/docs/TASK_EXECUTION.md#小批量集成).
These show scope-aware Lua dependency analysis, commit-based incremental
measurements and a reviewed exception process. Reuse the applicable concepts
and the project's own scripts and configuration. Additional languages,
runtime loaders, and packaging systems need their own validated setup.
