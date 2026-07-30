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

from importlib import metadata
import reny.cli.base.vchk
from reny.cli.base.bmp_options import BatchMPArgParser, BatchMPBaseCommands


class BatchMPDispatcher:
    ''' Base BatchMP Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = BatchMPArgParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args['sub_cmd'] == BatchMPBaseCommands.VERSION:
            self.print_version()

        elif args['sub_cmd'] == BatchMPBaseCommands.INFO:
            self.print_info()

        elif args['sub_cmd'] == BatchMPBaseCommands.IGNORE:
            self.generate_ignore(args.get('global_ignore', False), args.get('dir', '.'))

        elif args['sub_cmd'] == BatchMPBaseCommands.CONFIG:
            self.generate_config(args.get('local_config', False), args.get('dir', '.'))

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_version(self):
        ''' Prints version info
        '''
        version = metadata.version("reny")
        print('Reny version {}'.format(version))

    def print_info(self):
        print('\n{}'.format(self.option_parser.script_name.capitalize()))
        print(self.option_parser.description)

    def generate_ignore(self, is_global, target_dir):
        import os
        import sys
        import shutil
        template_src = os.path.join(os.path.dirname(__file__), 'renyignore.template')

        if not os.path.exists(template_src):
            print("Reny: error: Could not find renyignore.template")
            return

        target_path = os.path.expanduser('~/.renyignore') if is_global else os.path.join(target_dir, '.renyignore')
        if os.path.exists(target_path):
            print(f"Ignore file: {target_path}")
            editor = os.environ.get('EDITOR') or os.environ.get('VISUAL') or 'nvim'
            if sys.stdout.isatty():
                os.system(f"{editor} '{target_path}'")
            return

        shutil.copy(template_src, target_path)
        print(f"Successfully generated ignore template at: {target_path}")

    def generate_config(self, is_local, target_dir):
        import os
        import sys
        import shutil
        template_src = os.path.join(os.path.dirname(__file__), 'renyconfig.template')

        if not os.path.exists(template_src):
            print("Reny: error: Could not find renyconfig.template")
            return

        if is_local:
            target_path = os.path.join(target_dir, '.reny.toml')
        else:
            config_dir = os.path.expanduser('~/.config/reny')
            os.makedirs(config_dir, exist_ok=True)
            target_path = os.path.join(config_dir, 'config.toml')

        if os.path.exists(target_path):
            print(f"Config file: {target_path}")
            editor = os.environ.get('EDITOR') or os.environ.get('VISUAL') or 'nvim'
            if sys.stdout.isatty():
                os.system(f"{editor} '{target_path}'")
            return

        shutil.copy(template_src, target_path)
        print(f"Successfully generated template at: {target_path}")

def main():
    ''' BatchMP entry point
    '''
    BatchMPDispatcher().dispatch()

if __name__ == '__main__':
    main()

