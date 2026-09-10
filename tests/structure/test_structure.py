import os
import tempfile
import unittest

from reny.fstools.builders.fsprms import FSEntryParamsExt, FSEntryParamsOrganize
from reny.structure.flatten import FolderFlattener
from reny.structure.organize import DirectoryOrganizer


class TestStructureSubsystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_folder_flattener(self):
        # Create nested structure: src/level1/level2/nested.txt
        level1 = os.path.join(self.src_dir, 'level1')
        level2 = os.path.join(level1, 'level2')
        os.makedirs(level2)
        nested_file = os.path.join(level2, 'nested.txt')
        with open(nested_file, 'w') as f:
            f.write('content')

        params = FSEntryParamsExt()
        params.src_dir = self.src_dir
        params.target_level = 0
        params.quiet = True
        params.remove_folders = True
        params.remove_non_empty_folders = False

        files_cnt, dirs_cnt = FolderFlattener.flatten(params)
        self.assertEqual(files_cnt, 1)
        # Verify file moved to src_dir
        self.assertTrue(os.path.exists(os.path.join(self.src_dir, 'nested.txt')))
        # Verify empty nested directories were removed
        self.assertFalse(os.path.exists(level2))

    def test_directory_organizer_by_type(self):
        # Create files: photo.png, document.txt
        png_file = os.path.join(self.src_dir, 'photo.png')
        txt_file = os.path.join(self.src_dir, 'document.txt')
        with open(png_file, 'w') as f:
            f.write('png')
        with open(txt_file, 'w') as f:
            f.write('txt')

        params = FSEntryParamsOrganize()
        params.src_dir = self.src_dir
        params.by = 'type'
        params.quiet = True

        DirectoryOrganizer.organize(params)

        self.assertTrue(os.path.exists(os.path.join(self.src_dir, 'png', 'photo.png')))
        self.assertTrue(os.path.exists(os.path.join(self.src_dir, 'txt', 'document.txt')))
