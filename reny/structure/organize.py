"""Directory organization subsystem for Reny."""

import os
from reny.fstools.builders.fsentry import FSEntryType
from reny.fstools.fsutils import FSH
from reny.core.walker import DirectoryWalker
from reny.fstools.virtual_organizer import VirtualOrganizer
from reny.commons.progressbar import progress_bar, CmdProgressBarRefreshRate


class DirectoryOrganizer:
    """Organizes files into target folder hierarchies based on attributes (e.g. type, date)."""

    @staticmethod
    def organize(fs_entry_params):
        from reny.fstools.dirtools import DHandler

        organizer = VirtualOrganizer(fs_entry_params)
        if not organizer.build_virtual_structure():
            print("Nothing to process")
            return

        virtual_walker = organizer.organize_virtual_walker()
        max_depth = organizer.max_directory_depth()
        preview_params = organizer.organize_preview_params(max_depth)
        entries_to_process = list(DirectoryWalker.entries(fs_entry_params))
        fcnt = sum(1 for entry in entries_to_process if entry.type == FSEntryType.FILE and hasattr(entry, 'target_path'))

        if fs_entry_params.quiet:
            proceed = True
        else:
            proceed, _, _ = DHandler.visualise_changes(
                preview_params, virtual_walker, fs_preprocess_entry_params=fs_entry_params
            )

        if proceed and fcnt > 0:
            moved_files_cnt = 0
            with progress_bar(refresh_rate=CmdProgressBarRefreshRate.FAST) as p_bar:
                p_bar.info_msg = f'Organizing {fcnt} files'
                for entry in entries_to_process:
                    if entry.type == FSEntryType.FILE and hasattr(entry, 'target_path'):
                        target_dir = os.path.dirname(entry.target_path)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                        if FSH.move_FS_entry(entry.realpath, entry.target_path):
                            moved_files_cnt += 1
                    if fcnt > 0:
                        p_bar.progress += 100 / fcnt

            if not fs_entry_params.quiet:
                print(f'Organized: {moved_files_cnt} files')
                print('\nDone')

    @staticmethod
    def print_view(fs_entry_params):
        from reny.fstools.dirtools import DHandler

        organizer = VirtualOrganizer(fs_entry_params)
        if not organizer.build_virtual_structure():
            print("No files to organize view")
            return

        virtual_walker = organizer.print_virtual_walker()
        size_formatter = organizer.print_formatter_with_sizes()
        max_depth = organizer.max_directory_depth()
        preview_params = organizer.print_preview_params(max_depth)

        print(f"Virtual view by {fs_entry_params.by}:")
        DHandler.print_dir(preview_params, virtual_walker, formatter=size_formatter)
