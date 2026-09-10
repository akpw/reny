#!/usr/bin/env python
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


""" Batch renaming of files and directories
      . supports source directory / source file modes
      . visualises original / targeted folders structure before actual processing
      . supports recursion to specified end_level
      . supports flattening folders beyond specified end_level
      . allows for include / exclude patterns (Unix style)
      . allows global include/exclude of directories and folders
      . display sorting:
          .. by size/date, ascending/descending
      . action commands:
          .. print      Prints source directory
          .. index      Adds index to files and directories names
          .. add_date   Adds date to files and directories names
          .. add_text   Adds text to files and directories names
          .. remove     Removes n characters from files and directories names
          .. replace    RegExp-based replace in files and directories names,
                                        with support for expandable templates
          .. capitalize Capitalizes words in files / directories names
          .. flatten    Flatten all folders below target level, moving the files up
                            at the target level. By default, deletes all empty flattened folders
          .. delete     Delete selected files and directories

    Usage: renamer [-h] [-d DIR] [-f FILE] [GLobal Options] {Commands}[Commands Options]
      Input source mode:
        [-d, --dir]                 Source directory (default is the current directory)
        [-f, --file]                File to process

      Recursion mode:
        [-r, --recursive]           Recurse into nested folders
        [-el, --end-level]          End level for recursion into nested folders

      Filter files or folders:
        [-in, --include]            Include: Unix-style name patterns separated by ';'
        [-ex, --exclude]            Exclude: Unix-style name patterns separated by ';'
                                      (excludes hidden files by default)
        [-fd, --filter-dirs]        Enable  Include/Exclude patterns on directories
        [-af, --all-files]          Disable Include/Exclude patterns on files
                                      (shows hidden files excluded by default)
      Miscellaneous:
        [-s, --sort]{na|nd|sa|sd}   Sort order for files / folders (name | date, asc | desc)
        [-ni, nested-indent]        Indent for printing nested directories
        [-q, --quiet]               Do not visualise changes / show messages during processing

      Commands:
        {print, index, add_date, add_text, remove, replace, capitalize, flatten, delete, version, info}
        epilog = '''Usage examples:
        $ reny {command} -h  #run this for detailed help on individual commands
        '''"""
import sys
from argparse import SUPPRESS
from reny.cli.base.bmp_options import BatchMPArgParser, BatchMPHelpFormatter, BatchMPBaseCommands


class RenamerCommands(BatchMPBaseCommands):
    INDEX = 'index'
    ADD_DATE = 'add_date'
    ADD_TEXT = 'add_text'
    REMOVE = 'remove'
    REPLACE = 'replace'
    CAPITALIZE = 'capitalize'
    FLATTEN = 'flatten'
    DELETE = 'delete'
    STATS = 'stats'
    ORGANIZE = 'organize'
    PAD = 'pad'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.INDEX),
                        '{}, '.format(cls.ADD_DATE),
                        '{}, '.format(cls.ADD_TEXT),
                        '{}, '.format(cls.REMOVE),
                        '{}, '.format(cls.REPLACE),
                        '{}, '.format(cls.CAPITALIZE),
                        '{}, '.format(cls.FLATTEN),
                        '{}, '.format(cls.DELETE),
                        '{}, '.format(cls.STATS),
                        '{}, '.format(cls.INFO),
                        '{}, '.format(cls.IGNORE),
                        '{}, '.format(cls.CONFIG),
                        '{}, '.format(cls.VERSION),
                        '{}, '.format(cls.ORGANIZE),
                        '{}'  .format(cls.PAD),
                        '}'))


class RenameArgParser(BatchMPArgParser):
    ''' Reny commands parsing
    '''
    def __init__(self):
        self._script_name = 'Reny'

        self._description = '''
        Reny is a lightweight but powerful filesystem visualizer, batch renamer and organization CLI tool.
        It visualizes complex directory structures and generates virtual views, alongside 
        handling standard renaming tasks (regex replace, padding, appending text/dates) and advanced 
        operations like multi-level indexing and folder flattening. By default, Reny safely visualizes 
        all targeted changes and requires confirmation before modifying the filesystem.
        '''
    # Args Parsing
    def parse_commands(self, parser):
        ''' Reny commands parsing
        '''
        # Commands
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                                title = 'Reny Commands',
                                                metavar = '<command>')
        common = self._get_subcommand_common_parser()

        self._add_version(subparsers)
        self._add_info(subparsers)
        self._add_ignore(subparsers)
        self._add_config(subparsers)

        def _add_include_mode_group(parser):
            include_mode_group = parser.add_argument_group('Include for processing')
            include_mode_group.add_argument("-id", "--include-dirs", dest = "include_dirs",
                help = "Include directories for processing",
                action = 'store_true')
            include_mode_group.add_argument("-ef", "--exclude-files", dest = "exclude_files",
                help = "Exclude files from processing",
                action = 'store_true')

        # Print (default)
        print_parser = subparsers.add_parser(RenamerCommands.PRINT,
                                                description = 'Print source directory tree and file listing',
                                                help = 'Print directory tree (default command)',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        print_media_group = print_parser.add_argument_group('File media types')
        print_media_group.add_argument("-ft", "--file-type", dest = "file_type",
                    help = "File Media Type",
                    type = str,
                    choices = ['image', 'video', 'audio', 'media', 'nonmedia', 'playable', 'nonplayable', 'any'],
                    default = SUPPRESS)
        print_view_group = print_parser.add_argument_group('Virtual Views & Organization')
        print_view_group.add_argument('-b', '--by', dest = 'by',
                help = 'Organization strategy or virtual view by type or date',
                type = str,
                choices = ['type', 'date'],
                default = SUPPRESS)
        print_view_group.add_argument('-df', '--date-format', dest = 'date_format',
                help = 'Date format for subdirectories when using -b date (e.g., %%Y/%%m)',
                type = str,
                default = SUPPRESS)
        print_tree_group = print_parser.add_argument_group('Tree display')
        print_tree_group.add_argument("-ss", "--show-size", dest = 'show_size',
                    help = "Show files size",
                    action = 'store_true',
                    default = SUPPRESS)
        print_tree_group.add_argument('-ni', '--nested_indent', dest = 'nested_indent',
                    help = "Indent for printing nested directories",
                    type = str,
                    default = SUPPRESS)

        # Stats
        stats_parser = subparsers.add_parser(RenamerCommands.STATS,
                                                description = 'Prints directory stats',
                                                help = 'Print overall directory statistics',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        stats_media_group = stats_parser.add_argument_group('File media types')
        stats_media_group.add_argument("-ft", "--file-type", dest = "file_type",
                    help = "File Media Type",
                    type = str,
                    choices = ['image', 'video', 'audio', 'media', 'nonmedia', 'playable', 'nonplayable', 'any'],
                    default = SUPPRESS)

        # Flatten
        flatten_parser = subparsers.add_parser(RenamerCommands.FLATTEN,
                description = 'Flatten all folders below target level, moving the files up the target level. ' \
                              'By default, all empty flattened folders will be deleted.',
                help = 'Flatten folder hierarchies below target level',
                parents = [common],
                formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(flatten_parser)
        flatten_group = flatten_parser.add_argument_group('Flatten Options')
        flatten_group.add_argument('-tl', '--target-level', dest = 'target_level',
                help = 'Target level below which all folders will be flattened',
                type = int,
                required = True)
        flatten_group.add_argument('-dfl', '--discard-flattened', dest = 'discard_flattened',
                help = "What to do with flattened directories: " \
                       "'de' (default) will remove flattened directories if they are empty " \
                       "'le' will leave flattened directories (empty or not) " \
                       "'da' will discard flattened directories even if they are not empty",
                type=str,
                choices = ['de', 'le', 'da'],
                default = 'de')
        self._add_arg_display_curent_state_mode(flatten_group)

        # Add index
        add_index_parser = subparsers.add_parser(RenamerCommands.INDEX,
                                                 description = 'Adds index to files and directories names',
                                                 help = 'Add sequential or directory-scoped numeric indices',
                                                 parents = [common],
                                                 formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(add_index_parser)
        index_group = add_index_parser.add_argument_group('Index Options')
        index_group.add_argument('-sf', '--start-from', dest = 'start_from',
                help = 'A number from which the indexing starts (1 by default)',
                type = int,
                default = 1)
        add_index_type_group = index_group.add_mutually_exclusive_group()
        add_index_type_group.add_argument('-sq', '--sequential', dest = 'sequential',
                help = 'Index selected files sequentially across selected directores. ' \
                       'If omitted, the files will instead be indexed within their respective directories (multi-level indexing)',
                action = 'store_true')
        add_index_type_group.add_argument('-bd', '--by-directory', dest = 'by_directory',
                help = 'Index selected files via adding their respective directory counter. ' \
                       'If omitted, the files will instead be indexed within their respective directories (multi-level indexing)',
                action = 'store_true')
        index_group.add_argument('-as', '--as-suffix', dest = 'as_suffix',
                help = 'Add index at the end of file names',
                action = 'store_true')
        index_group.add_argument('-js', '--join-string', dest = 'join_str',
                help = "Join string for appending indices (' ' by default)",
                type = str,
                default = ' ')
        index_group.add_argument('-md', '--min-digits', dest = 'min_digits',
                help = 'Minimal number of digits for indexing (2 by default, and adding leading zeros as needed)',
                type = int,
                default = 2)
        self._add_arg_display_curent_state_mode(index_group)

        # Pad Numbers
        pad_parser = subparsers.add_parser(RenamerCommands.PAD,
                                                description = 'Pads numbers in files and directories names with leading zeros',
                                                help = 'Pad numbers with leading zeros',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(pad_parser)
        pad_group = pad_parser.add_argument_group('Pad Options')
        pad_group.add_argument('-md', '--min-digits', dest = 'min_digits',
                help = 'Minimal number of digits to pad to (2 by default, and adding leading zeros as needed)',
                type = int,
                default = 2)
        self._add_arg_display_curent_state_mode(pad_group)

        # Add Date
        add_date_parser = subparsers.add_parser(RenamerCommands.ADD_DATE,
                                                description = 'Adds date to files and directories names',
                                                help = 'Add formatted date as prefix or suffix',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(add_date_parser)
        date_group = add_date_parser.add_argument_group('Add Date Options')
        date_group.add_argument('-ap', '--as-prefix', dest = 'as_prefix',
                help = 'Add date as a prefix to file names',
                action = 'store_true')
        date_group.add_argument('-js', '--join-string', dest = 'join_str',
                help = "Join string for appending dates ('_' by default)",
                type = str,
                default = '_')
        date_group.add_argument('-fm', '--format', dest = 'format',
                help = 'Date format',
                type = str,
                default = '%Y-%m-%d')
        self._add_arg_display_curent_state_mode(date_group)

        # Add Text
        add_text_parser = subparsers.add_parser(RenamerCommands.ADD_TEXT,
                                                description = 'Adds text to files and directories names',
                                                help = 'Add arbitrary text as prefix or suffix',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(add_text_parser)
        text_group = add_text_parser.add_argument_group('Add Text Options')
        text_group.add_argument('-ap', '--asprefix', dest = 'as_prefix',
                help = 'Add text as a prefix to file names',
                action = 'store_true')
        text_group.add_argument('-js', '--join-string', dest = 'join_str',
                help = "Join string for appending text ('_' by default)",
                type = str,
                default = '_')
        text_group.add_argument('-tx', '--text', dest = 'text',
                help = 'Text to add',
                type = str,
                required = True)
        self._add_arg_display_curent_state_mode(text_group)

        # Remove chars
        remove_chars_parser = subparsers.add_parser(RenamerCommands.REMOVE,
                                            description = 'Removes n characters from files and directories names',
                                            help = 'Remove N characters from name head or tail',
                                            parents = [common],
                                            formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(remove_chars_parser)
        remove_group = remove_chars_parser.add_argument_group('Remove Options')
        remove_group.add_argument('-nc', '--num-chars', dest = 'num_chars',
                help = "Number of characters to remove",
                type = int,
                required = True)
        remove_group.add_argument('-ft', '--from-tail', dest = 'from_tail',
                help = 'Removes text from tail',
                action = 'store_true')
        self._add_arg_display_curent_state_mode(remove_group)

        # Replace
        replace_parser = subparsers.add_parser(RenamerCommands.REPLACE,
                                            description = 'RegExp-based replace in files and directories names. ' \
                                                   'Supports expandable templates, such as ' \
                                                   '$dirname, $pardirname, $atime, $ctime, etc.',
                                            help = 'Regexp-based find and replace with templates',
                                            parents = [common],
                                            formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(replace_parser)
        replace_group = replace_parser.add_argument_group('Replace Options')
        replace_group.add_argument('-fs', '--find-string', dest = 'find_str',
                help = "Find pattern to look for",
                type = str,
                required=True)
        replace_group.add_argument('-rs', '--replace-string', dest = 'replace_str',
                help = 'Replace pattern to replace with. ' \
                        'If not specified and there is a match from the find pattern, ' \
                        'the entire string will be replaced with that match. ' \
                        'Supports expandable templates: $dirname, $pardirname, $mdate, etc.',
                type = str)
        replace_group.add_argument('-ic', '--ignore-case', dest = 'ignore_case',
                help = 'Case insensitive',
                action = 'store_true')
        replace_group.add_argument('-ie', '--include-extension', dest = 'include_extension',
                help = 'Include file extension',
                action = 'store_true')
        self._add_arg_display_curent_state_mode(replace_group)

        # Capitalize
        capitalize_parser = subparsers.add_parser(RenamerCommands.CAPITALIZE,
                                                description = 'Capitalizes words in files / directories names',
                                                help = 'Capitalize words in file and directory names',
                                                parents = [common],
                                                formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(capitalize_parser)
        cap_group = capitalize_parser.add_argument_group('Capitalize Options')
        self._add_arg_display_curent_state_mode(cap_group)

        # Delete
        delete_parser = subparsers.add_parser(RenamerCommands.DELETE,
                                            description = 'Delete selected files and directories',
                                            help = 'Delete selected files and directories',
                                            parents = [common],
                                            formatter_class = BatchMPHelpFormatter)
        _add_include_mode_group(delete_parser)
        del_group = delete_parser.add_argument_group('Delete Options')
        self._add_arg_display_curent_state_mode(del_group)

        # Organize
        organize_parser = subparsers.add_parser(RenamerCommands.ORGANIZE,
                                            description='Organize selected files into directories by specified attributes',
                                            help='Organize files into subdirectories by type or date',
                                            parents = [common],
                                            formatter_class=BatchMPHelpFormatter)
        _add_include_mode_group(organize_parser)
        org_group = organize_parser.add_argument_group('Organize Options')
        org_group.add_argument('-b', '--by', dest='by',
                               help='Organization strategy or virtual view by type or date',
                               type=str,
                               choices=['type', 'date'],
                               required=True)
        org_group.add_argument('-df', '--date-format', dest='date_format',
                               help='Date format for subdirectories when using -b date (e.g., %%Y/%%m)',
                               type=str,
                               default='%Y-%m-%d')
        org_group.add_argument('-td', '--target-dir', dest='target_dir',
                               help='Target directory to organize files into',
                               type=str)
        self._add_arg_display_curent_state_mode(org_group)

    # Args Checking
    def default_command(self, args, parser):
        args['sub_cmd'] = RenamerCommands.PRINT

    def check_args(self, args, parser):
        ''' Validation of supplied Renamer CLI arguments
        '''
        super().check_args(args, parser)

        # Validate subcommand compatibility with global CLI options
        if ('-b' in sys.argv or '--by' in sys.argv) and args['sub_cmd'] not in (RenamerCommands.PRINT, RenamerCommands.ORGANIZE):
            parser.error(f"argument -b/--by is not supported for command '{args['sub_cmd']}'")

        if ('-df' in sys.argv or '--date-format' in sys.argv) and args['sub_cmd'] not in (RenamerCommands.PRINT, RenamerCommands.ORGANIZE):
            parser.error(f"argument -df/--date-format is not supported for command '{args['sub_cmd']}'")

        if ('-ss' in sys.argv or '--show-size' in sys.argv) and args['sub_cmd'] != RenamerCommands.PRINT:
            parser.error(f"argument -ss/--show-size is not supported for command '{args['sub_cmd']}'")

        if ('-ni' in sys.argv or '--nested_indent' in sys.argv) and args['sub_cmd'] != RenamerCommands.PRINT:
            parser.error(f"argument -ni/--nested_indent is not supported for command '{args['sub_cmd']}'")

        if ('-ft' in sys.argv or '--file-type' in sys.argv) and args['sub_cmd'] not in (RenamerCommands.PRINT, RenamerCommands.STATS):
            parser.error(f"argument -ft/--file-type is not supported for command '{args['sub_cmd']}'")

        if args['sub_cmd'] == RenamerCommands.FLATTEN:
            if args['file']:
                parser.error('This operation requires a source directory')
            if '-el' not in sys.argv and '--end-level' not in sys.argv:
                args['end_level'] = sys.maxsize
            elif args['end_level'] <= args['target_level']:
                args['end_level'] = args['target_level']

        if args['sub_cmd'] == RenamerCommands.ORGANIZE:
            if not args.get('by'):
                parser.error('argument -b/--by is required for the organize command')





