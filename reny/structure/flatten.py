"""Directory flattening subsystem for Reny."""

import os
from reny.fstools.builders.fsentry import FSEntryType
from reny.fstools.builders.fsprms import FSEntryParamsExt
from reny.fstools.fsutils import FSH
from reny.core.walker import DirectoryWalker


class FolderFlattener:
    """Flattens directory hierarchies below target level into target parent directories."""

    @staticmethod
    def flatten(ff_entry_params, remove_folders: bool = True, remove_non_empty_folders: bool = False):
        from reny.fstools.dirtools import DHandler

        fs_preprocess_entry_params = FSEntryParamsExt()
        fs_preprocess_entry_params.copy_params(ff_entry_params)

        if ff_entry_params.quiet:
            proceed = True
        else:
            proceed, _, _ = DHandler.visualise_changes(
                ff_entry_params, fs_preprocess_entry_params=fs_preprocess_entry_params
            )

        if proceed:
            flattened_dirs_cnt = flattened_files_cnt = 0
            target_dir_path = ''
            for entry in DirectoryWalker.entries(ff_entry_params):
                if entry.type in (FSEntryType.DIR, FSEntryType.ROOT):
                    if FSH.level_from_root(ff_entry_params.src_dir, entry.realpath) == ff_entry_params.target_level:
                        target_dir_path = entry.realpath
                else:
                    if target_dir_path and (FSH.level_from_root(ff_entry_params.src_dir, entry.realpath) - 1 > ff_entry_params.target_level):
                        target_fpath = os.path.join(target_dir_path, entry.basename)
                        if FSH.move_FS_entry(entry.realpath, target_fpath):
                            flattened_files_cnt += 1

            if ff_entry_params.remove_folders:
                flattened_dirs_cnt = FSH.remove_folders_below_target_level(
                    ff_entry_params.src_dir,
                    target_level=ff_entry_params.target_level,
                    empty_only=not ff_entry_params.remove_non_empty_folders,
                    non_empty_msg=getattr(ff_entry_params, 'non_empty_folders_mgs', 'Use --discard-flattened parameter to remove non empty folders'),
                )

            if not ff_entry_params.quiet:
                print('Flattened: {0} files, {1} folders'.format(flattened_files_cnt, flattened_dirs_cnt))
                print('\nDone')

            return flattened_files_cnt, flattened_dirs_cnt

        return 0, 0
