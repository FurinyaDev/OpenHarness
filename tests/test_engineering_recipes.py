import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import git, make_repo


SIZE_CHECK = Path(__file__).resolve().parents[1] / 'docs/examples/check_pr_size.py'


class SizeRecipeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = make_repo(directory.name)
        self.base = git(self.root, 'rev-parse', 'HEAD')

    def commit(self):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-m', 'fixture')
        return git(self.root, 'rev-parse', 'HEAD')

    def check(self, head, lines=3, files=2):
        return subprocess.run(
            [sys.executable, str(SIZE_CHECK), self.base, head,
             '--max-lines', str(lines), '--max-files', str(files)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def test_git_counts_text_changes_and_both_paths_of_a_move(self):
        git(self.root, 'mv', 'file.txt', 'moved file.txt')
        (self.root / 'one more.txt').write_text('more\n', encoding='utf-8')
        head = self.commit()
        passing = self.check(head, files=3)
        self.assertEqual(0, passing.returncode, passing.stderr)
        self.assertIn('3 text lines (+/-) in 3 files', passing.stdout)
        for limits in ({'files': 2}, {'lines': 2, 'files': 3}):
            with self.subTest(limits=limits):
                failing = self.check(head, **limits)
                self.assertEqual(1, failing.returncode, failing.stderr)
                self.assertIn('Size budget exceeded', failing.stderr)

    def test_binary_and_missing_commit_fail_for_their_own_reasons(self):
        (self.root / 'plot.bin').write_bytes(b'\0binary')
        binary = self.check(self.commit())
        self.assertEqual(1, binary.returncode, binary.stderr)
        self.assertIn("Binary change: b'plot.bin'", binary.stderr)
        missing = self.check('a' * 40)
        self.assertEqual(2, missing.returncode, missing.stderr)
        self.assertIn('Size check incomplete', missing.stderr)
