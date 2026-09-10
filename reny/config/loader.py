"""TOML configuration loader for Reny.

Loads default configuration from .reny.toml (local) or ~/.config/reny/config.toml (global)
and injects defaults into parsed CLI arguments where CLI flags were not explicitly provided.
"""

import os
import sys
from typing import Optional, List


def resolve_config_path(target_dir: str = '.') -> Optional[str]:
    """Resolves the configuration file path (local has precedence over global)."""
    local_config = os.path.join(target_dir, '.reny.toml')
    global_config = os.path.expanduser('~/.config/reny/config.toml')

    if os.path.exists(local_config):
        return local_config
    if os.path.exists(global_config):
        return global_config

    return None


def load_config_defaults(args: dict, argv: Optional[List[str]] = None) -> None:
    """Loads default settings from ~/.config/reny/config.toml or ./.reny.toml into args."""
    if os.environ.get('DISABLE_CONFIG_FOR_TESTS') == '1':
        return

    if argv is None:
        argv = sys.argv

    target_dir = args.get('dir', '.')
    config_path = resolve_config_path(target_dir)
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

        if 'recursive' in recursion and '-r' not in argv and '--recursive' not in argv:
            args['recursive'] = bool(recursion['recursive'])
        if 'start_level' in recursion and '-sl' not in argv and '--start-level' not in argv:
            args['start_level'] = int(recursion['start_level'])
        if 'end_level' in recursion and '-el' not in argv and '--end-level' not in argv:
            args['end_level'] = int(recursion['end_level'])

        if 'include' in filtering and isinstance(filtering['include'], list) and filtering['include'] and '-in' not in argv and '--include' not in argv:
            args['include'] = ';'.join(filtering['include'])
        if 'exclude' in filtering and isinstance(filtering['exclude'], list) and filtering['exclude'] and '-ex' not in argv and '--exclude' not in argv:
            args['exclude'] = ';'.join(filtering['exclude'])
        if 'ignore_file' in filtering and filtering['ignore_file'] and '-ig' not in argv and '--ignore-file' not in argv:
            args['ignore_file'] = filtering['ignore_file']
        if 'all_dirs' in filtering and '-ad' not in argv and '--all-dirs' not in argv:
            args['all_dirs'] = bool(filtering['all_dirs'])
        if 'all_files' in filtering and '-af' not in argv and '--all-files' not in argv:
            args['all_files'] = bool(filtering['all_files'])

        if 'file_type' in media and '-ft' not in argv and '--file-type' not in argv:
            args['file_type'] = media['file_type']

        if 'show_size' in views and '-ss' not in argv and '--show-size' not in argv:
            args['show_size'] = bool(views['show_size'])
        if 'by' in views and '-b' not in argv and '--by' not in argv:
            args['by'] = views['by']
        if 'date_format' in views and '-df' not in argv and '--date-format' not in argv:
            args['date_format'] = views['date_format']

        if 'sort' in misc and '-s' not in argv and '--sort' not in argv:
            args['sort'] = misc['sort']
        if 'nested_indent' in misc and '-ni' not in argv and '--nested_indent' not in argv:
            args['nested_indent'] = misc['nested_indent']
        if 'quiet' in misc and '-q' not in argv and '--quiet' not in argv:
            args['quiet'] = bool(misc['quiet'])
        if 'color' in misc and '-c' not in argv and '--color' not in argv:
            args['color'] = int(misc['color'])
        if 'git' in misc and '-g' not in argv and '--git' not in argv:
            args['git'] = bool(misc['git'])
        elif 'git' in cfg.get('defaults', {}) and '-g' not in argv and '--git' not in argv:
            args['git'] = bool(cfg['defaults']['git'])
    except Exception:
        pass
