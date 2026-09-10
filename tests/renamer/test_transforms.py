import datetime
import os
import tempfile
import unittest

from reny.fstools.builders.fsentry import FSEntry, FSEntryType
from reny.renamer.transforms import (
    build_pad_transform,
    build_date_transform,
    build_add_text_transform,
    build_remove_n_chars_transform,
    build_capitalize_transform,
    build_replace_transform,
    expand_templates,
)


class TestRenamerTransforms(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, 'photo 1.jpg')
        with open(self.file_path, 'w') as f:
            f.write('data')

        self.file_entry = FSEntry(
            type=FSEntryType.FILE,
            basename='photo 1.jpg',
            realpath=self.file_path,
            indent='',
        )
        self.dir_entry = FSEntry(
            type=FSEntryType.DIR,
            basename='vacation 2024',
            realpath=self.temp_dir.name,
            indent='',
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pad_transform(self):
        pad_fn = build_pad_transform(min_digits=3)
        self.assertEqual(pad_fn(self.file_entry), 'photo 001.jpg')

    def test_capitalize_transform(self):
        cap_fn = build_capitalize_transform()
        self.assertEqual(cap_fn(self.file_entry), 'Photo 1.jpg')
        self.assertEqual(cap_fn(self.dir_entry), 'Vacation 2024')

    def test_add_text_prefix_and_suffix(self):
        prefix_fn = build_add_text_transform('Trip', as_prefix=True, join_str='_')
        self.assertEqual(prefix_fn(self.file_entry), 'Trip_photo 1.jpg')

        suffix_fn = build_add_text_transform('Final', as_prefix=False, join_str='-')
        self.assertEqual(suffix_fn(self.file_entry), 'photo 1-Final.jpg')

    def test_remove_n_chars(self):
        head_fn = build_remove_n_chars_transform(num_chars=6, from_head=True)
        self.assertEqual(head_fn(self.file_entry), '1.jpg')

        tail_fn = build_remove_n_chars_transform(num_chars=2, from_head=False)
        self.assertEqual(tail_fn(self.file_entry), 'photo.jpg')

    def test_add_date(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        date_fn = build_date_transform(as_prefix=True, join_str='_')
        self.assertEqual(date_fn(self.file_entry), f'{today}_photo 1.jpg')

    def test_replace_transform(self):
        replace_fn = build_replace_transform(find_str=r'photo\s+(\d+)', replace_str=r'img_\1')
        self.assertEqual(replace_fn(self.file_entry), 'img_1.jpg')

    def test_template_expansion(self):
        expanded = expand_templates(self.file_entry, '$dirname-$mdate')
        self.assertIn(os.path.basename(self.temp_dir.name), expanded)
