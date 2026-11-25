# Preserving project acceptance

In a strict installation, the project can add `verification.acceptance_paths` to
`.harness/config.json`. List the exact tracked files that express a proven
acceptance criterion, including the suite entry point, assertions and any fixture
or loader whose change could bypass the criterion. Ordinary test files can stay
outside this list. The profile's existing material inputs and environment fields
continue to define which inputs the candidate evidence covers.

```json
{
  "acceptance_paths": [
    "tests/acceptance/test_startup.py",
    "scripts/verify-startup.py",
    "tests/fixtures/production-profile.json"
  ]
}
```

The trusted verifier reads this list from the current canonical base. An edit,
rename or deletion of a listed file takes the existing exact-head/base control
approval path before any candidate acceptance runs. The proposed declaration must
refer to tracked regular files in the candidate. `entry` exposes the locally
declared paths for discovery. Live enforcement requires a compatible immutable
controller pin and current native deployment proof. Roll out the controller
through the existing governed upgrade path before adding the declaration. Use
the project's existing native controls in cooperative installations.

For a replacement, record the preserved behavior and its evidence in the work
item or PR. An approved configuration change runs both configurations against the
candidate. To exercise the old assertions independently of the candidate's test
files, keep the old probe in the pinned image or in the trusted baseline argv
where appropriate. Demonstrate that the proposed replacement accepts the fixed
behavior and detects the original failure. The path guard covers the files the
project designates. Review owns equivalence, dependencies outside those files and
the impact of approved contract changes.

## Incident follow-through

1. Preserve the accepted behavior, the failing case and its successor in the
   existing Issue or PR. Run the same relevant workload against the reproduced
   failure and the intended fixed candidate. Confirm that the failure reaches the
   expected assertion and that the normal path passes.
2. Record what actually ran. Bind source/base or resulting tree, material
   production-profile inputs, verifier and environment. For a release claim, use
   the project's release receipt to connect the published artifact digest to its
   source and external verification. Record why runs with different workload
   inputs are unpaired. Preserve missing, failed and exempt results in the receipt.
3. Reconcile the behavior, regression test and active CI entry point on the
   continuing target. Verify the integrated tree and the actual required check on
   that target. An earlier release branch or a merge record alone cannot supply
   this evidence. Keep unresolved items in the existing work authority.
4. For emergency publication, retain the exact waived gate, owner decision,
   accepted scope and outstanding validation in that same work item. Restore the
   ordinary gate and run its verification on the appropriate subject. The
   OpenHarness integration status covers the repository candidate. The project
   owns release receipts, external acceptance and emergency publication policy.
