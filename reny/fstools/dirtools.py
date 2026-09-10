# coding=utf8
## Copyright (c) 2014 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.


import os, sys, subprocess
from collections import namedtuple
from collections.abc import Iterable
from reny.commons.utils import strtobool
import pygtrie
from reny.core.walker import DirectoryWalker as DWalker
from reny.fstools.fsutils import FSH
from reny.fstools.builders.fsentry import FSEntry, FSEntryType, FSEntryDefaults
from reny.fstools.builders.fsprms import FSEntryParamsExt, FSEntryParamsOrganize
from reny.commons.progressbar import progress_bar, CmdProgressBarRefreshRate
from reny.fstools.virtual_organizer import VirtualOrganizer
from reny.view.styler import style_entry
from reny.view.formatters import format_git_badge, format_size_badge, format_summary, format_total_size
# from profilehooks import profile


class DHandler:
    ''' FS Directory level utilities
    '''
    @staticmethod
#    @profile
    def print_dir(fs_entry_params, walker=os.walk, formatter = None, selected_files_description = None):
        """ Prints content of given directory
            Supports additional display name processing via formatter supplied by the caller
        """
        if not os.path.exists(fs_entry_params.src_dir):
            raise ValueError('Not a valid path')

        if formatter is None:
            formatter = lambda entry: entry.basename

        if selected_files_description is None:
            selected_files_description = 'file'

        # print the dir tree
        fcnt = dcnt = 0
        total_size = 0
        shared_cache = {}

        for entry in DWalker.entries(fs_entry_params, walker):
            # get formatted output
            formatted_output = ''
            if isinstance(formatter, Iterable):
                for chained_formatter in formatter:
                    chained_formatter_output = chained_formatter(entry)
                    formatted_output = '{0}{1}'.format(
                            formatted_output if formatted_output else '',
                            chained_formatter_output if chained_formatter_output else '')
            else:
                formatted_output = formatter(entry)

            if formatted_output:
                git_indicator = ''
                if getattr(fs_entry_params, 'git', False) and entry.type != FSEntryType.ROOT:
                    if hasattr(fs_entry_params, '_init_git') and not getattr(fs_entry_params, '_git_initialized', False):
                        fs_entry_params._init_git()
                    if getattr(fs_entry_params, '_git_initialized', False):
                        status = fs_entry_params.git_statuses.get(os.path.normpath(entry.realpath).lower())
                        git_indicator = format_git_badge(status)

                size = ''
                if entry.type == FSEntryType.FILE:
                    fcnt += 1
                    if fs_entry_params.show_size:
                        fsize = os.path.getsize(entry.realpath)
                        size = format_size_badge(fsize)
                        total_size += fsize
                elif entry.type == FSEntryType.DIR and not entry.isEnclosingEntry:
                    dcnt += 1
                    if fs_entry_params.show_size:
                        display_size = FSH.dir_size(entry.realpath, shared_cache = shared_cache)
                        size = format_size_badge(display_size)

                        if FSH.level_from_root(fs_entry_params.src_dir, entry.realpath) <= fs_entry_params.end_level:
                            dsize = os.path.getsize(entry.realpath)
                        else:
                            dsize = display_size

                        total_size += dsize

                formatted_output = style_entry(
                    formatted_output, entry.type, filename=entry.basename,
                    color_enabled=bool(getattr(fs_entry_params, 'color', 1))
                )

                print('{0}{1}{2}{3}'.format(entry.indent, size, formatted_output, git_indicator))

        # print summary
        print(format_summary(fcnt, dcnt, description=selected_files_description))

        if fs_entry_params.show_size and total_size > 0:
            print(format_total_size(total_size))

        return fcnt, dcnt

    @staticmethod
    def stats(fs_entry_params):
        print('Overall directory statistics might take a while...')
        print(fs_entry_params.src_dir)        

        total_files, total_dirs, total_size = DHandler.dir_stats(fs_entry_params)
        
        print('{0}Total files: {1}'.format(FSEntryDefaults.DEFAULT_NESTED_INDENT, total_files))
        print('{0}Total directores: {1}'.format(FSEntryDefaults.DEFAULT_NESTED_INDENT, total_dirs))
        if fs_entry_params.show_size: 
            print('{0}Total size: {1}'.format(FSEntryDefaults.DEFAULT_NESTED_INDENT, FSH.fs_size(total_size)))

    @staticmethod
    def dir_stats(fs_entry_params, 
                    file_pass_filter = None, dir_pass_filter = None, break_on_filter = False):
        """ Returns base stats for given directory
        """
        if not os.path.exists(fs_entry_params.src_dir):
            raise ValueError('Not a valid path')

        # count number of files, folders, and their total size
        shared_cache = {}
        fcnt = dcnt = total_size = 0
        for entry in DWalker.entries(fs_entry_params):
            if entry.type == FSEntryType.FILE:
                if file_pass_filter and (not file_pass_filter(entry)):
                    if break_on_filter:
                        break
                    continue                    
                fcnt += 1
                if fs_entry_params.show_size:
                    total_size += os.path.getsize(entry.realpath)

            elif entry.type == FSEntryType.DIR:
                if entry.isEnclosingEntry:
                    continue
                if dir_pass_filter and (not dir_pass_filter(entry)):
                    if break_on_filter:
                        break                    
                    continue

                dcnt += 1
                if fs_entry_params.show_size:
                    if FSH.level_from_root(fs_entry_params.src_dir, entry.realpath) <= fs_entry_params.end_level:
                        total_size += os.path.getsize(entry.realpath)
                    else:
                        total_size += FSH.dir_size(entry.realpath, shared_cache = shared_cache)

        return fcnt, dcnt, total_size

    @staticmethod
    def get_user_input(quiet = False):
        ''' Displays confirmation promt and gathers users' input
        '''
        answer = input('\nProceed? [y/n]: ')
        try:
            answer = True if strtobool(answer) else False
        except ValueError:
            print('Not confirmative, exiting')
            return False

        if not quiet:
            if answer:
                print('Confirmed, processing...')
            else:
                print('Not confirmed, exiting')

        return answer

    @staticmethod
    def visualise_changes(fs_entry_params, walker=os.walk,
                            before_msg = 'Current source directory:',
                            after_msg = 'Targeted after processing:',                
                            preformatter = None, formatter = None, reset_formatters = None,
                            selected_files_description = None, fs_preprocess_entry_params = None):

        ''' Displays targeted changes and gets users' confirmation on futher processing
        '''
        if not fs_preprocess_entry_params: 
            fs_preprocess_entry_params = fs_entry_params

        if fs_preprocess_entry_params.display_current:
            print(before_msg)
            DHandler.print_dir(fs_preprocess_entry_params, os.walk,
                                formatter = preformatter,
                                selected_files_description = selected_files_description)
            if reset_formatters:
                reset_formatters()
            print()

        print(after_msg)
        fcnt, dcnt = DHandler.print_dir(fs_entry_params, walker,
                                            formatter = formatter,
                                            selected_files_description = selected_files_description)
        if fcnt == dcnt == 0:
            print ('Nothing to process')
            return False, fcnt, dcnt
        else:
            return DHandler.get_user_input(), fcnt, dcnt

    @staticmethod
    def flatten_folders(ff_entry_params, 
                        remove_folders = True, remove_non_empty_folders = False):
        ''' Flattens all folders below target level, moving the files up at the target level
        '''
        from reny.structure.flatten import FolderFlattener
        return FolderFlattener.flatten(ff_entry_params, remove_folders=remove_folders, remove_non_empty_folders=remove_non_empty_folders)

    @staticmethod
    def rename_entries(fs_entry_params,
                        num_entries = 0,
                        formatter = None, check_unique = True):
        """ Renames directory entries via applying formatter function supplied by the caller
        """
        if not formatter or num_entries <= 0:
            return

        fcnt = dcnt = 0
        DirEntry = namedtuple('DirEntry', ['orig_path', 'target_path'])
        dir_entries = []
        
        with progress_bar(refresh_rate = CmdProgressBarRefreshRate.FAST) as p_bar:
            p_bar.info_msg = 'Renaming {} entries'.format(num_entries)

            for entry in DWalker.entries(fs_entry_params):
                if entry.type == FSEntryType.ROOT:
                    continue

                target_name = formatter(entry)
                if target_name == entry.basename:
                    continue

                target_path = os.path.join(os.path.dirname(entry.realpath), target_name)

                if entry.type == FSEntryType.DIR:
                    # for dirs, need to postpone
                    dir_entries.append(DirEntry(entry.realpath, target_path))

                elif entry.type == FSEntryType.FILE:
                    # for files, just rename
                    if FSH.move_FS_entry(entry.realpath, target_path, check_unique = check_unique):
                        fcnt += 1

                p_bar.progress += 100 / num_entries

        #rename the dirs
        for dir_entry in reversed(dir_entries):
            if FSH.move_FS_entry(dir_entry.orig_path, dir_entry.target_path, check_unique = check_unique):
                dcnt += 1

        # print summary
        if not fs_entry_params.quiet:
            print('Renamed: {0} files, {1} folders'.format(fcnt, dcnt))

    @staticmethod
    def remove_entries(fs_entry_params, formatter = None):
        """ Removes entries with formatter function supplied by the caller
        """
        if not formatter:
            return

        fcnt = dcnt = 0
        dir_entries = []
        for entry in DWalker.entries(fs_entry_params):

            if entry.type == FSEntryType.ROOT or (entry.type == FSEntryType.DIR and entry.isEnclosingEntry):
                continue

            if formatter(entry) is None:
                continue

            if entry.type == FSEntryType.DIR:
                # for dirs, need to postpone
                dir_entries.append(entry.realpath)

            elif entry.type == FSEntryType.FILE:
                # for files, OK to remove now
                FSH.remove_FS_entry(entry.realpath)
                fcnt += 1

        #rename the dirs
        for dir_entry in reversed(dir_entries):
            FSH.remove_FS_entry(dir_entry)
            dcnt += 1

        # print summary
        if not fs_entry_params.quiet:
            print('Removed: {0} files, {1} folders'.format(fcnt, dcnt))

    @staticmethod
    def organize(fs_entry_params):
        """ Organizes files into subdirectories based on specified attributes
        """
        from reny.structure.organize import DirectoryOrganizer
        return DirectoryOrganizer.organize(fs_entry_params)

    @staticmethod
    def print_organized_view(fs_entry_params):
        """ Print hierarchical organized-like virtual view
        """
        from reny.structure.organize import DirectoryOrganizer
        return DirectoryOrganizer.print_view(fs_entry_params)



