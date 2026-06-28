import unittest
import os
import sys
import tempfile
from unittest.mock import patch
from reny.cli.base.bmp_options import BatchMPArgParser

class TestIgnoreOptions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.temp_dir.name
        
    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('sys.argv', ['reny', '-d', 'DUMMY_DIR', 'info'])
    def test_local_ignore(self):
        sys.argv[2] = self.dir_path
        
        # Create local .renyignore
        ignore_path = os.path.join(self.dir_path, '.renyignore')
        with open(ignore_path, 'w') as f:
            f.write("local_ignore1\nlocal_ignore2\n")
            
        parser = BatchMPArgParser()
        args = parser.parse_options()
        self.assertIn("local_ignore1;local_ignore2", args['exclude'])

    @patch('sys.argv', ['reny', '-d', 'DUMMY_DIR', 'info'])
    def test_global_ignore(self):
        sys.argv[2] = self.dir_path
        
        global_ignore_path = os.path.join(self.dir_path, '.global_renyignore')
        with open(global_ignore_path, 'w') as f:
            f.write("global_ignore1\nglobal_ignore2\n")
            
        original_expanduser = os.path.expanduser
        def mock_expanduser(path):
            return global_ignore_path if path == '~/.renyignore' else original_expanduser(path)
            
        with patch('os.path.expanduser', side_effect=mock_expanduser):
            parser = BatchMPArgParser()
            args = parser.parse_options()
            self.assertIn("global_ignore1;global_ignore2", args['exclude'])

    @patch('sys.argv', ['reny', '-d', 'DUMMY_DIR', '-ig', 'custom.txt', 'info'])
    def test_custom_ignore(self):
        sys.argv[2] = self.dir_path
        
        custom_ignore_path = os.path.join(self.dir_path, 'custom.txt')
        with open(custom_ignore_path, 'w') as f:
            f.write("custom_ignore1\ncustom_ignore2\n")
            
        parser = BatchMPArgParser()
        args = parser.parse_options()
        self.assertIn("custom_ignore1;custom_ignore2", args['exclude'])
        
    @patch('sys.argv', ['reny', '-d', 'DUMMY_DIR', 'info'])
    def test_local_takes_precedence_over_global(self):
        sys.argv[2] = self.dir_path
        
        local_ignore_path = os.path.join(self.dir_path, '.renyignore')
        with open(local_ignore_path, 'w') as f:
            f.write("local_ignore\n")
            
        global_ignore_path = os.path.join(self.dir_path, '.global_renyignore')
        with open(global_ignore_path, 'w') as f:
            f.write("global_ignore\n")
            
        original_expanduser = os.path.expanduser
        def mock_expanduser(path):
            return global_ignore_path if path == '~/.renyignore' else original_expanduser(path)
            
        with patch('os.path.expanduser', side_effect=mock_expanduser):
            parser = BatchMPArgParser()
            args = parser.parse_options()
            self.assertIn("local_ignore", args['exclude'])
            self.assertNotIn("global_ignore", args['exclude'])
