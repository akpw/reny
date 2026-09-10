# coding=utf8
import os
import unittest
import tempfile
import time

from reny.core.filter import glob_match, passes_glob_patterns
from reny.core.sorter import sort_filenames, sort_dirnames


class FilterTests(unittest.TestCase):
    def test_glob_match(self):
        self.assertTrue(glob_match('test.py', '*.py'))
        self.assertTrue(glob_match('test.png', '*.jpg;*.png;*.gif'))
        self.assertFalse(glob_match('test.txt', '*.jpg;*.png'))
        self.assertFalse(glob_match('test.py', ''))

    def test_passes_glob_patterns(self):
        self.assertTrue(passes_glob_patterns('app.py', include_patterns='*.py', exclude_patterns='.*'))
        self.assertFalse(passes_glob_patterns('.hidden.py', include_patterns='*.py', exclude_patterns='.*'))
        self.assertFalse(passes_glob_patterns('app.log', include_patterns='*.py', exclude_patterns='.*'))


class SorterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dpath = self.temp_dir.name

        # Create files with varying names, sizes, and timestamps
        self.f1 = os.path.join(self.dpath, 'a_small.txt')
        with open(self.f1, 'w') as f:
            f.write('small')

        time.sleep(0.01)

        self.f2 = os.path.join(self.dpath, 'b_large.txt')
        with open(self.f2, 'w') as f:
            f.write('large content here!')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sort_filenames_by_name(self):
        files = ['b_large.txt', 'a_small.txt']
        sorted_files = sort_filenames(files, self.dpath, by_size=False, by_date=False, descending=False)
        self.assertEqual(sorted_files, ['a_small.txt', 'b_large.txt'])

        rev = sort_filenames(files, self.dpath, by_size=False, by_date=False, descending=True)
        self.assertEqual(rev, ['b_large.txt', 'a_small.txt'])

    def test_sort_filenames_by_size(self):
        files = ['b_large.txt', 'a_small.txt']
        sorted_files = sort_filenames(files, self.dpath, by_size=True, descending=False)
        self.assertEqual(sorted_files, ['a_small.txt', 'b_large.txt'])

        sorted_rev = sort_filenames(files, self.dpath, by_size=True, descending=True)
        self.assertEqual(sorted_rev, ['b_large.txt', 'a_small.txt'])

    def test_sort_filenames_by_date(self):
        files = ['b_large.txt', 'a_small.txt']
        sorted_files = sort_filenames(files, self.dpath, by_date=True, descending=False)
        self.assertEqual(sorted_files, ['a_small.txt', 'b_large.txt'])
