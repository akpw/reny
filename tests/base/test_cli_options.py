import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from io import StringIO

from reny.cli.renamer.renamer_options import RenameArgParser


class TestCLIOptions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_subcommand_table_in_main_help(self):
        parser = RenameArgParser()
        arg_parser = parser._get_parser() if hasattr(parser, '_get_parser') else None
        
        # Capture root help
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            with self.assertRaises(SystemExit):
                with patch.object(sys, 'argv', ['reny', '-h']):
                    parser.parse_options()

        help_output = stdout.getvalue()
        self.assertIn('Reny Commands:', help_output)
        self.assertIn('Pad numbers with leading zeros', help_output)
        self.assertIn('Print directory tree (default command)', help_output)
        self.assertIn('Flatten folder hierarchies below target level', help_output)

    def test_position_independent_options(self):
        parser = RenameArgParser()
        # Pass -d AFTER subcommand
        with patch.object(sys, 'argv', ['reny', 'pad', '-d', self.dir_path, '-md', '4', '-q']):
            args = parser.parse_options()

        self.assertEqual(args['sub_cmd'], 'pad')
        self.assertEqual(args['dir'], os.path.realpath(self.dir_path))
        self.assertEqual(args['min_digits'], 4)
        self.assertTrue(args['quiet'])

    def test_subcommand_help_includes_common_options(self):
        parser = RenameArgParser()
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            with self.assertRaises(SystemExit):
                with patch.object(sys, 'argv', ['reny', 'pad', '-h']):
                    parser.parse_options()

        help_output = stdout.getvalue()
        self.assertIn('Input source mode:', help_output)
        self.assertIn('Recursion mode:', help_output)
        self.assertIn('Filter files or folders:', help_output)
        self.assertIn('-d, --dir DIR', help_output)
        self.assertIn('-r, --recursive', help_output)
        self.assertIn('-md, --min-digits MIN_DIGITS', help_output)

        # Ensure global options appear before command-specific options
        misc_idx = help_output.index('Miscellaneous:')
        pad_idx = help_output.index('Pad Options:')
        self.assertLess(misc_idx, pad_idx)

        # Ensure filtered options like -b/--by do not appear in pad help
        self.assertNotIn('Virtual Views & Organization:', help_output)

    def test_incompatible_global_options_rejected(self):
        parser = RenameArgParser()
        # -b is not supported for index
        with patch.object(sys, 'argv', ['reny', '-b', 'type', 'index']):
            with self.assertRaises(SystemExit):
                parser.parse_options()

        # -ss is not supported for pad
        with patch.object(sys, 'argv', ['reny', '-ss', 'pad']):
            with self.assertRaises(SystemExit):
                parser.parse_options()
