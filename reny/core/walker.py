"""Filesystem traversal generator for Reny.

Walks directory trees yielding structured FSEntry elements.
Decouples directory walking and entry emission from legacy descriptor side-effects.
"""

import os
from typing import Callable, Generator, Optional
from reny.fstools.builders.fsentry import FSEntry, FSEntryType


def walk_entries(fs_entry_params, walker: Callable = os.walk) -> Generator[FSEntry, None, None]:
    """Generates a sequence of FSEntry elements by traversing the directory tree."""
    for rpath, dnames, fnames in walker(fs_entry_params.src_dir):
        # Update current path
        fs_entry_params.rpath = rpath

        # Check recursion depth bounds
        if fs_entry_params.skip_iteration:
            continue

        # Set siblings (triggers filtering and sorting)
        fs_entry_params.fnames = fnames
        fs_entry_params.dnames = dnames

        # Sync pruned/sorted directory names back to os.walk in-place
        dnames[:] = fs_entry_params.merged_dnames

        # Yield folder entry
        yield from fs_entry_params.fs_entry_builder.build_root_entry(fs_entry_params)

        # Yield contained files / directory leaf entries
        yield from fs_entry_params.fs_entry_builder.build_entry(fs_entry_params)


def walk_files(fs_entry_params, pass_filter: Optional[Callable[[str], bool]] = None) -> Generator[FSEntry, None, None]:
    """Yields only file FSEntry elements matching the optional path filter."""
    if not pass_filter:
        pass_filter = lambda f: True

    for entry in walk_entries(fs_entry_params):
        if entry.type in (FSEntryType.ROOT, FSEntryType.DIR):
            continue
        if pass_filter(entry.realpath):
            yield entry


def walk_dirs(fs_entry_params, pass_filter: Optional[Callable[[str], bool]] = None) -> Generator[FSEntry, None, None]:
    """Yields only directory FSEntry elements matching the optional path filter."""
    if not pass_filter:
        pass_filter = lambda f: True

    for entry in walk_entries(fs_entry_params):
        if entry.type in (FSEntryType.ROOT, FSEntryType.FILE):
            continue
        if pass_filter(entry.realpath):
            yield entry


class DirectoryWalker:
    """Class wrapper matching DWalker interface."""
    entries = staticmethod(walk_entries)
    file_entries = staticmethod(walk_files)
    dir_entries = staticmethod(walk_dirs)


# Alias for backward compatibility
DWalker = DirectoryWalker

__all__ = ['DirectoryWalker', 'DWalker', 'walk_entries', 'walk_files', 'walk_dirs']

