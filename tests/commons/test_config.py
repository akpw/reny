import unittest
import os
import sys
import tempfile
from unittest.mock import patch
from reny.cli.base.bmp_options import BatchMPArgParser

class TestConfigOptions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_config_defaults(self):
        config_path = os.path.join(self.dir_path, '.reny.toml')
        with open(config_path, 'w') as f:
            f.write('[recursion]\nend_level = 2\n\n[misc]\ngit = true\n')

        args = {'dir': self.dir_path, 'end_level': 0, 'git': False, 'sub_cmd': 'info'}
        
        with patch.dict(os.environ, {'DISABLE_CONFIG_FOR_TESTS': '0'}):
            BatchMPArgParser.load_config_defaults(args)
            
        self.assertEqual(args['end_level'], 2)
        self.assertTrue(args['git'])

    def test_cli_overrides_config(self):
        config_path = os.path.join(self.dir_path, '.reny.toml')
        with open(config_path, 'w') as f:
            f.write('[recursion]\nend_level = 2\n\n[misc]\ngit = true\n')

        args = {'dir': self.dir_path, 'end_level': 0, 'git': False, 'sub_cmd': 'info'}

        # Simulate CLI passing -el 0 explicitly
        with patch.object(sys, 'argv', ['reny', '-d', self.dir_path, '-el', '0', 'info']):
            with patch.dict(os.environ, {'DISABLE_CONFIG_FOR_TESTS': '0'}):
                BatchMPArgParser.load_config_defaults(args)

        self.assertEqual(args['end_level'], 0)
