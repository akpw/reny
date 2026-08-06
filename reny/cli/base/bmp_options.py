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


""" Global options parsing:
        [-r, --recursive]           Recurse into nested folders
        [-el, --end-level]          End level for recursion into nested folders

        [-in, --include]            Include names pattern (Unix style)
        [-ex, --exclude]            Exclude names pattern (Unix style)
                                      (excludes hidden files by default)
        [-ad, --all-dirs]           Prevent using Include/Exclude patterns on directories
        [-af, --all-files]          Prevent using Include/Exclude patterns on files
                                      (shows hidden files excluded by default)

        [-s, --sort]{na|nd|sa|sd}   Sort order for files / folders (name | date, asc | desc)
        [-ni, nested-indent]        Indent for printing nested directories
        [-q, --quiet]               Do not visualise changes / show messages during processing
"""

import os, sys, string
from argparse import ArgumentParser, HelpFormatter
from reny.commons.utils import strtobool
from urllib.parse import urlparse
from reny.commons.utils import MiscHelpers
from reny.fstools.fsutils import FSH
from reny.fstools.builders.fsentry import FSEntry, FSEntryDefaults



class BatchMPBaseCommands:
    VERSION = 'version'
    INFO = 'info'
    IGNORE = 'ignore'
    CONFIG = 'config'
    PRINT = 'print'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.INFO),
                        '{}, '.format(cls.IGNORE),
                        '{}, '.format(cls.CONFIG),
                        '{}'.format(cls.VERSION),
                        '}'))

class BatchMPArgParser:
    def __init__(self):
        self._script_name = 'Reny'
        self._description = '''
    Reny provides management of files, directories, etc...

    Reny tools consist of three main command-line utilities.
    For more information, run:
        $ renamer -h
        $ tagger -h
        $ bmfp -h
    '''

    @property
    def description(self):
        return self._description

    @property
    def script_name(self):
        return self._script_name

    # Args parsing
    def parse_options(self):
        ''' Common workflow for parsing options
        '''
        parser = ArgumentParser(prog = self._script_name, description = self._description,
                                                                formatter_class=BatchMPHelpFormatter)

        self.parse_global_options(parser)

        self.parse_commands(parser)

        args = vars(parser.parse_args())

        self.check_args(args, parser)

        return args

    def parse_global_options(self, parser):
        ''' Parses global options
        '''
        source_mode_group = parser.add_argument_group('Input source mode')
        source_mode_group.add_argument("-d", "--dir", dest = "dir",
                    type = lambda d: self._is_valid_dir_path(parser, d),
                    help = "Source directory (default is current directory)",
                    default = os.curdir)
        source_mode_group.add_argument("-f", "--file", dest = "file",
                    type = lambda f: self._is_valid_file_path(parser, f),
                    help = "File to process")

        recursive_mode_group = parser.add_argument_group('Recursion mode')
        recursive_mode_group.add_argument('-r', '--recursive', dest = 'recursive',
                help = 'Recursive mode (optional if -el is specified)',
                action = 'store_true')
        recursive_mode_group.add_argument('-sl', '--start-level', dest = 'start_level',
                help = 'Initial nested level for printing (0, i.e. root source directory by default)',
                type = int,
                default = 0)
        recursive_mode_group.add_argument("-el", "--end-level", dest = "end_level",
                help = "Target level for recursive descent (makes -r optional, automatically adjusts to match -sl if smaller)",
                type = int,
                default = 0)

        include_mode_group = parser.add_argument_group('Filter files or folders')
        include_mode_group.add_argument("-in", "--include", dest = "include",
                    help = "Include: Unix-style name patterns separated by ';'",
                    type = str,
                    default =  FSEntryDefaults.DEFAULT_INCLUDE)
        include_mode_group.add_argument("-ex", "--exclude", dest = "exclude",
                    help = "Exclude: Unix-style name patterns separated by ';' (excludes hidden files by default)",
                    type = str,
                    default =  FSEntryDefaults.DEFAULT_EXCLUDE)
        include_mode_group.add_argument("-ig", "--ignore-file", dest = "ignore_file",
                    help = "Ignore file: Read Unix-style name patterns from a custom file",
                    type = str,
                    default = None)
        include_mode_group.add_argument("-ad", "--all-dirs", dest = "all_dirs",
                    help = "Disable Include/Exclude patterns on directories",
                    action = 'store_true')
        include_mode_group.add_argument("-af", "--all-files", dest = "all_files",
                    help = "Disable Include/Exclude patterns on files (shows hidden files excluded by default)",
                    action = 'store_true')

        media_types_group = parser.add_argument_group('File media types')
        media_types_group.add_argument("-ft", "--file-type", dest = "file_type",
                    help = "File Media Type",
                    type = str,
                    choices = ['image', 'video', 'audio', 'media', 'nonmedia', 'playable', 'nonplayable', 'any'],
                    default =  FSEntryDefaults.DEFAULT_FILE_TYPE)

        view_org_group = parser.add_argument_group('Virtual Views & Organization')
        view_org_group.add_argument('-ss', '--show-size', dest = 'show_size',
                help ='Show files size',
                action = 'store_true')
        view_org_group.add_argument('-b', '--by', dest = 'by',
                help = 'Organization strategy or virtual view by type or date',
                type = str,
                choices = ['type', 'date'])
        view_org_group.add_argument('-df', '--date-format', dest = 'date_format',
                help = 'Date format for subdirectories when using -b date (e.g., %%Y/%%m)',
                type = str,
                default = '%Y-%m-%d')


        # Add Default Miscellaneous Group
        self._add_arg_misc_group(parser)

    def parse_commands(self, parser):
        ''' Specific commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                            title = 'BatchMP commands',
                                                metavar = BatchMPBaseCommands.commands_meta())
        self._add_version(subparsers)
        self._add_info(subparsers)
        self._add_ignore(subparsers)
        self._add_config(subparsers)

    # Args checking
    def check_cmd_args(self, args, parser,
                        show_help = False,
                        exit = False):
        if not args.get('sub_cmd'):
            if show_help:
                parser.print_help()
            if exit:
                sys.exit(1)

            # if not exiting, need to default
            self.default_command(args, parser)

    def default_command(self, args, parser):
        args['sub_cmd'] = BatchMPBaseCommands.INFO

    @staticmethod
    def load_config_defaults(args):
        """Loads default settings from ~/.config/reny/config.toml or ./.reny.toml"""
        if os.environ.get('DISABLE_CONFIG_FOR_TESTS') == '1':
            return

        config_path = None
        target_dir = args.get('dir', '.')
        local_config = os.path.join(target_dir, '.reny.toml')
        global_config = os.path.expanduser('~/.config/reny/config.toml')

        if os.path.exists(local_config):
            config_path = local_config
        elif os.path.exists(global_config):
            config_path = global_config

        if not config_path:
            return

        try:
            if sys.version_info >= (3, 11):
                import tomllib
                with open(config_path, 'rb') as f:
                    cfg = tomllib.load(f)
            else:
                return

            recursion = cfg.get('recursion', cfg.get('defaults', {}))
            filtering = cfg.get('filtering', {})
            media = cfg.get('media', {})
            views = cfg.get('views', {})
            misc = cfg.get('misc', {})

            if 'recursive' in recursion and '-r' not in sys.argv and '--recursive' not in sys.argv:
                args['recursive'] = bool(recursion['recursive'])
            if 'start_level' in recursion and '-sl' not in sys.argv and '--start-level' not in sys.argv:
                args['start_level'] = int(recursion['start_level'])
            if 'end_level' in recursion and '-el' not in sys.argv and '--end-level' not in sys.argv:
                args['end_level'] = int(recursion['end_level'])

            if 'include' in filtering and isinstance(filtering['include'], list) and filtering['include'] and '-in' not in sys.argv and '--include' not in sys.argv:
                args['include'] = ';'.join(filtering['include'])
            if 'exclude' in filtering and isinstance(filtering['exclude'], list) and filtering['exclude'] and '-ex' not in sys.argv and '--exclude' not in sys.argv:
                args['exclude'] = ';'.join(filtering['exclude'])
            if 'ignore_file' in filtering and filtering['ignore_file'] and '-ig' not in sys.argv and '--ignore-file' not in sys.argv:
                args['ignore_file'] = filtering['ignore_file']
            if 'all_dirs' in filtering and '-ad' not in sys.argv and '--all-dirs' not in sys.argv:
                args['all_dirs'] = bool(filtering['all_dirs'])
            if 'all_files' in filtering and '-af' not in sys.argv and '--all-files' not in sys.argv:
                args['all_files'] = bool(filtering['all_files'])

            if 'file_type' in media and '-ft' not in sys.argv and '--file-type' not in sys.argv:
                args['file_type'] = media['file_type']

            if 'show_size' in views and '-ss' not in sys.argv and '--show-size' not in sys.argv:
                args['show_size'] = bool(views['show_size'])
            if 'by' in views and '-b' not in sys.argv and '--by' not in sys.argv:
                args['by'] = views['by']
            if 'date_format' in views and '-df' not in sys.argv and '--date-format' not in sys.argv:
                args['date_format'] = views['date_format']

            if 'sort' in misc and '-s' not in sys.argv and '--sort' not in sys.argv:
                args['sort'] = misc['sort']
            if 'nested_indent' in misc and '-ni' not in sys.argv and '--nested_indent' not in sys.argv:
                args['nested_indent'] = misc['nested_indent']
            if 'quiet' in misc and '-q' not in sys.argv and '--quiet' not in sys.argv:
                args['quiet'] = bool(misc['quiet'])
            if 'color' in misc and '-c' not in sys.argv and '--color' not in sys.argv:
                args['color'] = int(misc['color'])
            if 'git' in misc and '-g' not in sys.argv and '--git' not in sys.argv:
                args['git'] = bool(misc['git'])
            elif 'git' in cfg.get('defaults', {}) and '-g' not in sys.argv and '--git' not in sys.argv:
                args['git'] = bool(cfg['defaults']['git'])
        except Exception:
            pass

    def check_args(self, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        self.check_cmd_args(args, parser)

        # load config defaults from ~/.config/reny/config.toml or ./.reny.toml
        self.load_config_defaults(args)

        # ignore file processing
        ignore_path = None
        if args.get('ignore_file'):
            ignore_path = os.path.abspath(args['ignore_file']) if os.path.isabs(args['ignore_file']) else os.path.join(args.get('dir', '.'), args['ignore_file'])
        else:
            local_ignore = os.path.join(args.get('dir', '.'), '.renyignore')
            if os.path.exists(local_ignore):
                ignore_path = local_ignore
            else:
                global_ignore = os.path.expanduser('~/.renyignore')
                if os.path.exists(global_ignore):
                    ignore_path = global_ignore

        if ignore_path and os.path.exists(ignore_path):
            with open(ignore_path, 'r') as f:
                patterns = [line.strip().rstrip('/') for line in f if line.strip() and not line.startswith('#')]
                if patterns:
                    ignore_str = ';'.join(patterns)
                    if args.get('exclude'):
                        args['exclude'] += ';' + ignore_str
                    else:
                        args['exclude'] = ignore_str

        # if input source is a file, need to adjust
        if args['file']:
            args['dir'] = os.path.dirname(args['file'])
            args['include'] = os.path.basename(args['file'])
            args['exclude'] = ''
            args['end_level'] = 0
            args['all_files'] = False
            args['all_dirs'] = False

        # check recursion
        if args['recursive'] and args['end_level'] == 0:
            args['end_level'] = sys.maxsize


        # (media_scan check removed)

        if args['sub_cmd'] == BatchMPBaseCommands.PRINT:
            if args['start_level'] != 0:
                if args['file']:
                    print ('Start Level parameter requires a source directory\n Ignoring requested Start Level...')
                    args['start_level'] = 0
                elif args['end_level'] < args['start_level']:
                    ''' print ('Start Level should be greater than or equal to the Recursion End Level Global Option\n'
                           '... Adjusting End Level to: {}'.format(args['start_level']))
                    '''
                    args['end_level'] = args['start_level']

    # Internal Helpers
    @staticmethod
    def _is_valid_dir_path(parser, path_arg):
        """ Checks if path_arg is a valid dir path
        """
        path_arg = FSH.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isdir(path_arg)):
            parser.error('"{}" does not seem to be an existing directory path'.format(path_arg))
        else:
            return path_arg

    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        """ Checks if path_arg is a valid file path
        """
        path_arg = FSH.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error('"{}" does not seem to be an existing file path'.format(path_arg))
        else:
            return path_arg

    @staticmethod
    def _is_boolean(parser, bool_arg):
        """ Checks if bool_arg can be interpreted as a boolean value
        """
        try:
            bool_arg = True if strtobool(bool_arg) else False
        except ValueError:
            parser.error('"{}": Please enter a boolean value'.format(bool_arg))
            return False

    @staticmethod
    def _is_valid_url(parser, url_arg):
        url_parts = urlparse(url_arg)

        def _parser_error():
            parser.error('"{}": Please enter a valid URL'.format(url_arg))

        if url_parts.scheme in (None, '') and url_parts.netloc in (None, ''):
            _parser_error()

        if url_parts.scheme == 'file':
            if url_parts.netloc == '~':
                fpath = '~{}'.format(url_parts.path)
            else:
                fpath = url_parts.path
            return BatchMPArgParser._is_valid_file_path(parser, fpath)

        if not set(url_parts.netloc).issubset(set(string.ascii_letters + string.digits + '-.')):
            _parser_error()

        if not url_parts.scheme in ['http', 'https', 'ftp', 'file']:
            _parser_error()

        return url_arg

    @staticmethod
    def _is_valid_url_or_file_path(parser, url_or_file_path_arg):
        url_parts = urlparse(url_or_file_path_arg)
        if url_parts.scheme in (None, '') and url_parts.netloc in (None, ''):
            return BatchMPArgParser._is_valid_file_path(parser, url_or_file_path_arg)
        else:
            return BatchMPArgParser._is_valid_url(parser, url_or_file_path_arg)

    @staticmethod
    def _is_timedelta(parser, td_arg):
        try:
            td = MiscHelpers.time_delta(td_arg)
        except ValueError:
            parser.error('"{}": Please enter a valid value, ' \
                         'in seconds or in the "hh:mm:ss[.xxx]" format'.format(td_arg))
        return  td

    # Processing mode for relevant commands
    @staticmethod
    def _add_arg_display_curent_state_mode(parser):
        parser.add_argument('-dc', '--display-current', dest = 'display_current',
                help ='Unless in quiet mode, display current (pre-processing) state in the confirmation propmt',
                action = 'store_true')

    @staticmethod
    def _add_arg_misc_group(parser):
        misc_group = parser.add_argument_group('Miscellaneous')
        misc_group.add_argument('-s', '--sort', dest = 'sort',
                    help = "Sorting for files ('na', i.e. by name ascending by default)",
                    type = str,
                    choices = ['na', 'nd', 'sa', 'sd'],
                    default = FSEntryDefaults.DEFAULT_SORT)
        misc_group.add_argument('-ni', '--nested_indent', dest = 'nested_indent',
                    help = "Indent for printing  nested directories",
                    type = str,
                    default = '  ')
        misc_group.add_argument("-q", "--quiet", dest = 'quiet',
                    help = "Disable visualising changes & displaying info messages during processing",
                    action = 'store_true')
        misc_group.add_argument("-c", "--color", dest="color", 
                    help="Color output (0 or 1, default 1)", 
                    type=int, choices=[0, 1], default=1)
        misc_group.add_argument("-g", "--git", dest="git", 
                    help="Show git status", 
                    action="store_true")
        misc_group.add_argument("-go", "--git-only", dest="git_only", 
                    help="Show only files with git status modifications", 
                    action="store_true")
        misc_group.add_argument("-gt", "--git-tracked", dest="git_tracked", 
                    help="Show only git tracked files", 
                    action="store_true")

    @staticmethod
    def _add_version(parser):
        ''' Adds the version command
        '''
        parser.add_parser(BatchMPBaseCommands.VERSION,
                                description = 'Displays BatchMP version info',
                                        formatter_class=BatchMPHelpFormatter)

    @staticmethod
    def _add_info(parser):
        ''' Adds the info command
        '''
        parser.add_parser(BatchMPBaseCommands.INFO,
                                description = 'Displays BatchMP info',
                                        formatter_class=BatchMPHelpFormatter)

    @staticmethod
    def _add_ignore(parser):
        ''' Adds the ignore command
        '''
        init_parser = parser.add_parser(BatchMPBaseCommands.IGNORE,
                                description = 'Generates a default .renyignore template file',
                                        formatter_class=BatchMPHelpFormatter)
        init_parser.add_argument('-gl', '--global', dest='global_ignore',
                                 action='store_true',
                                 help='Generate the template globally (~/.renyignore)')

    @staticmethod
    def _add_config(parser):
        ''' Adds the config command
        '''
        config_parser = parser.add_parser(BatchMPBaseCommands.CONFIG,
                                description = 'Generates a default config.toml template file (~/.config/reny/config.toml)',
                                        formatter_class=BatchMPHelpFormatter)
        config_parser.add_argument('-l', '--local', dest='local_config',
                                 action='store_true',
                                 help='Generate the config template locally (./.reny.toml)')



class BatchMPHelpFormatter(HelpFormatter):
    ''' Custom ArgumentParser formatter
        Disables double metavar display, showing it only for long-named options
    '''
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)
