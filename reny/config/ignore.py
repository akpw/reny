"""Ignore rules subsystem for Reny.

Handles discovery and parsing of .renyignore files (local and global)
and integrates them into exclusion filter patterns.
"""

import os
from typing import Optional, List
from reny.fstools.builders.fsentry import FSEntryDefaults


def resolve_ignore_file(target_dir: str = '.', custom_ignore: Optional[str] = None) -> Optional[str]:
    """Resolves the path to the active .renyignore file.
    
    Priority:
    1. Explicit custom ignore path
    2. Local .renyignore in target_dir
    3. Global ~/.renyignore in user home
    """
    if custom_ignore:
        if os.path.isabs(custom_ignore):
            return os.path.abspath(custom_ignore)
        return os.path.join(target_dir, custom_ignore)

    local_ignore = os.path.join(target_dir, '.renyignore')
    if os.path.exists(local_ignore):
        return local_ignore

    global_ignore = os.path.expanduser('~/.renyignore')
    if os.path.exists(global_ignore):
        return global_ignore

    return None


def load_ignore_patterns(ignore_path: str) -> List[str]:
    """Reads ignore patterns from a file, ignoring comments and blank lines."""
    if not ignore_path or not os.path.exists(ignore_path):
        return []

    try:
        with open(ignore_path, 'r', encoding='utf-8') as f:
            return [
                line.strip().rstrip('/')
                for line in f
                if line.strip() and not line.strip().startswith('#')
            ]
    except (IOError, OSError):
        return []


def apply_ignore_rules(args: dict) -> None:
    """Applies .renyignore rules into args['exclude'] dictionary."""
    target_dir = args.get('dir', '.')
    custom_ignore = args.get('ignore_file')
    ignore_path = resolve_ignore_file(target_dir, custom_ignore)

    # Skip .renyignore if we explicitly want to see ignored or untracked files
    if ignore_path and os.path.exists(ignore_path) and not args.get('git_ignored') and not args.get('not_git_tracked'):
        patterns = load_ignore_patterns(ignore_path)
        if patterns:
            ignore_str = ';'.join(patterns)
            if args.get('exclude'):
                args['exclude'] += ';' + ignore_str
            else:
                args['exclude'] = ignore_str

    if (args.get('git_ignored') or args.get('not_git_tracked')) and args.get('exclude') == FSEntryDefaults.DEFAULT_EXCLUDE:
        args['exclude'] = ''
