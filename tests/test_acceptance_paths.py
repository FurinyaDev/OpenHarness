import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openharness.ci import check_candidate
from openharness.model import default_config, validate_config
from openharness.repository import Repository
from openharness.runtime import Runtime
from tests.helpers import git, make_repo


CONTRACT = 'tests/test_acceptance.py'
REPLACEMENT = 'tests/test_closure.py'
ASSERTION = """from pathlib import Path
import unittest

class Contract(unittest.TestCase):
    def test_product_behavior(self):
        self.assertEqual('base', Path('file.txt').read_text().strip())
"""
BASELINE_CHECK = """from pathlib import Path
if Path('file.txt').read_text().strip() != 'base':
    raise SystemExit('BASELINE_CONTRACT')
"""


class AcceptancePathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'candidate'
        self.root.mkdir()
        make_repo(self.root)
        (self.root / 'file.txt').write_text('regressed\n', encoding='utf-8')
        self.before_contract = self.commit()
        self.baseline = self.root.parent / 'baseline'
        self.config = default_config('owner/repo', 'main')
        self.config['verification'].update(
            controller={'repository': 'tool/source', 'revision': 'c' * 40},
            sandbox_image='python@sha256:' + 'a' * 64,
            commands=[['python', '-B', '-m', 'unittest', 'discover', '-s', 'tests'],
                      ['python', '-B', '-c', BASELINE_CHECK]],
            acceptance_paths=[CONTRACT],
        )
        self.write_config(self.config)
        (self.root / 'tests').mkdir()
        (self.root / CONTRACT).write_text(ASSERTION, encoding='utf-8')
        (self.root / 'file.txt').write_text('base\n', encoding='utf-8')
        self.base = self.commit()
        git(self.root, 'worktree', 'add', '--detach', str(self.baseline), self.base)
        git(self.root, 'switch', '-c', 'codex/50-preserve')

    def write_config(self, config):
        path = self.root / '.harness/config.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(config), encoding='utf-8')

    def commit(self):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-m', 'synthetic change')
        return git(self.root, 'rev-parse', 'HEAD')

    def check(self, approval=None):
        head = git(self.root, 'rev-parse', 'HEAD')
        pull = {'number': 7, 'state': 'open', 'body': 'Work-Item: #50',
                'head': {'sha': head, 'ref': 'codex/50-preserve'},
                'base': {'sha': self.base, 'ref': 'main'}}
        endpoints = {
            'pulls/7': pull, 'branches/main': {'commit': {'sha': self.base}},
            'issues/50': {'state': 'open', 'number': 50},
            'issues/50/comments?per_page=100': [approval] if approval else [],
        }
        return check_candidate(
            Repository(self.baseline).config(), self.baseline, self.root,
            {'pull_request': {'number': 7}},
            lambda path: endpoints[path.removeprefix('repos/owner/repo/')],
        )

    def approval(self, head, base=None):
        return {'user': {'login': 'owner'},
                'body': f'OpenHarness-Control-Approval: {head} {base or self.base}'}

    def test_fresh_entry_discovers_declared_paths_without_live_state(self):
        result = Runtime(Repository(self.baseline)).entry()
        self.assertIsNone(result['workspace'])
        self.assertEqual('not-observed', result['assessment'])
        self.assertEqual([CONTRACT], result['declared_acceptance_paths'])

    def test_unauthorized_removal_skip_reversal_and_reconstruction_fail_before_tests(self):
        def reconstruct():
            git(self.root, 'restore', '--source=' + self.before_contract, '--staged', '--worktree', '.')

        path = self.root / CONTRACT
        mutations = {
            'removed': path.unlink,
            'skipped': lambda: path.write_text(ASSERTION.replace('    def test_', '    def skipped_'), encoding='utf-8'),
            'reversed': lambda: path.write_text(ASSERTION.replace('assertEqual', 'assertNotEqual'), encoding='utf-8'),
            'reconstructed': reconstruct,
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                git(self.root, 'reset', '--hard', self.base)
                (self.root / 'file.txt').write_text('regressed\n', encoding='utf-8')
                mutate()
                head = self.commit()
                with patch('openharness.ci.subprocess.run', wraps=subprocess.run) as run:
                    with self.assertRaisesRegex(ValueError, 'Protected control change'):
                        self.check(self.approval(head, self.before_contract))
                    self.assertFalse(any(call.args[0][0] == 'docker' for call in run.call_args_list))

    def test_unlisted_test_edits_still_use_candidate_acceptance(self):
        (self.root / 'tests/test_extra.py').write_text('import unittest\n', encoding='utf-8')
        self.commit()
        self.assertFalse(self.run_candidate()['control_authorized'])
        (self.root / 'file.txt').write_text('regressed\n', encoding='utf-8')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'Candidate acceptance failed'):
            self.run_candidate()

    def propose_replacement(self):
        git(self.root, 'mv', CONTRACT, REPLACEMENT)
        proposed = copy.deepcopy(self.config)
        proposed['verification']['acceptance_paths'] = [REPLACEMENT]
        proposed['verification']['commands'] = [
            [*self.config['verification']['commands'][0], '-p', 'test_closure.py'],
        ]
        self.write_config(proposed)

    def test_exact_approval_allows_equivalent_replacement_and_runs_both_configurations(self):
        self.propose_replacement()
        head = self.commit()
        result = self.run_candidate(self.approval(head))
        self.assertTrue(result['control_authorized'])
        checks = result['checks']
        self.assertEqual([*self.config['verification']['commands'],
                          Repository(self.root).config()['verification']['commands'][0]],
                         [item['argv'] for item in checks])
        self.assertIn('Ran 1 test', checks[0]['stderr'])
        self.assertIn('Ran 1 test', checks[2]['stderr'])

    def test_immutable_baseline_probe_still_rejects_approved_but_weakened_replacement(self):
        self.propose_replacement()
        (self.root / REPLACEMENT).write_text(ASSERTION.replace('assertEqual', 'assertNotEqual'), encoding='utf-8')
        (self.root / 'file.txt').write_text('regressed\n', encoding='utf-8')
        head = self.commit()
        with self.assertRaisesRegex(ValueError, 'BASELINE_CONTRACT'):
            self.run_candidate(self.approval(head))

    def test_approval_cannot_leave_a_dangling_declaration(self):
        (self.root / CONTRACT).unlink()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, 'Acceptance paths must exist'):
            self.check(self.approval(head))

    def test_damaged_target_can_recover_by_an_approved_restore(self):
        contract = self.root / CONTRACT
        contract.unlink()
        self.base = self.commit()
        git(self.baseline, 'checkout', '--detach', self.base)
        contract.parent.mkdir(exist_ok=True)
        contract.write_text(ASSERTION, encoding='utf-8')
        head = self.commit()
        self.assertTrue(self.run_candidate(self.approval(head))['control_authorized'])

    def test_proposed_declaration_is_checked_as_literal_regular_file(self):
        # A tracked directory and a missing wildcard cannot stand in for a contract.
        for path in ('tests', 'tests/test_*.py'):
            with self.subTest(path=path):
                proposed = copy.deepcopy(self.config)
                proposed['verification']['acceptance_paths'] = [path]
                self.write_config(proposed)
                head = self.commit()
                with self.assertRaisesRegex(ValueError, 'Acceptance paths must exist'):
                    self.check(self.approval(head))

    def run_candidate(self, approval=None):
        # Execute the synthetic Python tests without requiring Docker in the unit suite.
        # The production controller still constructs and uses its existing sandbox.
        run = subprocess.run

        def run_fixture(argv, *args, **kwargs):
            if argv[0] == 'docker':
                command = argv[argv.index(self.config['verification']['sandbox_image']) + 1:]
                return run([sys.executable, *command[1:]], *args, **kwargs, cwd=self.root)
            return run(argv, *args, **kwargs)

        with patch('openharness.ci.subprocess.run', side_effect=run_fixture):
            return self.check(approval)


class AcceptancePathConfigurationTests(unittest.TestCase):
    def test_declarations_reject_nonliteral_or_duplicate_paths_and_cooperative_mode(self):
        config = default_config('owner/repo', 'main')
        for paths in ([CONTRACT, CONTRACT], ['../contract'], ['tests//acceptance.py'],
                      ['/contract'], ['tests\\acceptance.py'], ['.git/config'], [7], CONTRACT):
            with self.subTest(paths=paths):
                config['verification']['acceptance_paths'] = paths
                with self.assertRaisesRegex(ValueError, 'literal repository-relative'):
                    validate_config(config)
        config['verification']['acceptance_paths'] = [CONTRACT]
        self.assertEqual(config, validate_config(config))
        config['mode'] = 'cooperative'
        with self.assertRaisesRegex(ValueError, 'strict trusted controller'):
            validate_config(config)
