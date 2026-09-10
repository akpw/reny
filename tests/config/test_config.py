import os
import tempfile
import unittest
from unittest.mock import patch

from reny.config.ignore import resolve_ignore_file, load_ignore_patterns, apply_ignore_rules
from reny.config.loader import resolve_config_path, load_config_defaults


class TestConfigSubsystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_resolve_ignore_file_priority(self):
        with patch('os.path.expanduser', return_value=os.path.join(self.dir_path, 'fake_global_ignore')):
            # 1. None when empty
            self.assertIsNone(resolve_ignore_file(self.dir_path))

            # 2. Local ignore
            local_path = os.path.join(self.dir_path, '.renyignore')
            with open(local_path, 'w') as f:
                f.write('*.log\n')
            self.assertEqual(resolve_ignore_file(self.dir_path), local_path)

            # 3. Custom ignore overrides local
            custom_path = os.path.join(self.dir_path, 'custom.ignore')
            with open(custom_path, 'w') as f:
                f.write('*.tmp\n')
            self.assertEqual(resolve_ignore_file(self.dir_path, 'custom.ignore'), custom_path)

    def test_load_ignore_patterns_stripping_and_comments(self):
        ignore_path = os.path.join(self.dir_path, '.renyignore')
        with open(ignore_path, 'w') as f:
            f.write('# comment\n\nbuild/\n  dist/  \n*.pyc\n')

        patterns = load_ignore_patterns(ignore_path)
        self.assertEqual(patterns, ['build', 'dist', '*.pyc'])

    def test_apply_ignore_rules_to_args(self):
        ignore_path = os.path.join(self.dir_path, '.renyignore')
        with open(ignore_path, 'w') as f:
            f.write('node_modules/\n.venv/\n')

        args = {'dir': self.dir_path, 'exclude': 'custom_*'}
        apply_ignore_rules(args)
        self.assertEqual(args['exclude'], 'custom_*;node_modules;.venv')

    def test_config_loader_resolution(self):
        config_path = os.path.join(self.dir_path, '.reny.toml')
        with open(config_path, 'w') as f:
            f.write('[recursion]\nend_level = 3\n[views]\nshow_size = true\n')

        args = {'dir': self.dir_path}
        with patch.dict(os.environ, {'DISABLE_CONFIG_FOR_TESTS': '0'}):
            load_config_defaults(args, argv=['reny'])

        self.assertEqual(args.get('end_level'), 3)
        self.assertTrue(args.get('show_size'))
