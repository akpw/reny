# coding=utf8
import os
import unittest
from unittest.mock import patch, MagicMock

from reny.core.git import GitStatusTracker


class GitStatusTrackerTests(unittest.TestCase):
    def test_tracker_none_safe(self):
        tracker = GitStatusTracker(None)
        self.assertIsNone(tracker.src_dir)
        tracker.init(git=True)
        self.assertFalse(tracker.is_git_repo)
        self.assertTrue(tracker.passed_filters('/some/path'))

    def test_tracker_non_git_repo(self):
        tracker = GitStatusTracker('/non/existent/path/probably')
        tracker.init(git=True)
        self.assertFalse(tracker.is_git_repo)
        self.assertTrue(tracker.passed_filters('/non/existent/path/probably/file.txt'))

    @patch('subprocess.run')
    def test_tracker_status_and_propagation(self, mock_run):
        def side_effect(cmd, **kwargs):
            m = MagicMock()
            if 'rev-parse' in cmd:
                m.returncode = 0
                m.stdout = '/repo\n'
            elif 'status' in cmd:
                m.returncode = 0
                m.stdout = ' M sub/nested/file.py\n?? untracked.txt\n'
            elif 'ls-files' in cmd:
                m.returncode = 0
                m.stdout = ''
            return m

        mock_run.side_effect = side_effect

        tracker = GitStatusTracker('/repo')
        tracker.init(git=True, git_only=True)

        self.assertTrue(tracker.is_git_repo)
        self.assertEqual(tracker.git_root, '/repo')

        # Direct status
        self.assertEqual(tracker.get_status('/repo/sub/nested/file.py'), ' M')
        self.assertEqual(tracker.get_status('/repo/untracked.txt'), '??')

        # Parent directory propagation
        self.assertEqual(tracker.get_status('/repo/sub/nested'), '* ')
        self.assertEqual(tracker.get_status('/repo/sub'), '* ')

        # Filter verification
        self.assertTrue(tracker.passed_filters('/repo/sub/nested/file.py', git_only=True))
        self.assertTrue(tracker.passed_filters('/repo/sub', is_dir=True, git_only=True))
        self.assertFalse(tracker.passed_filters('/repo/other/clean.py', git_only=True))
