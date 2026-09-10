# coding=utf8
"""
Reny Core Sorter: Pure sorting utilities for directory entries.
"""
import os
from typing import List
from reny.fstools.fsutils import FSH


def sort_filenames(
    fnames: List[str],
    rpath: str,
    by_size: bool = False,
    by_date: bool = False,
    descending: bool = False
) -> List[str]:
    """Sorts file names by size, date, or case-insensitive alphabetical order."""
    if by_size:
        sort_key = lambda fname: os.path.getsize(os.path.join(rpath, fname))
    elif by_date:
        sort_key = lambda fname: os.path.getmtime(os.path.join(rpath, fname))
    else:
        sort_key = lambda fname: fname.lower()
    return sorted(fnames, key=sort_key, reverse=descending)


def sort_dirnames(
    dnames: List[str],
    rpath: str,
    by_size: bool = False,
    by_date: bool = False,
    descending: bool = False
) -> List[str]:
    """Sorts directory names by cumulative size, modification date, or alphabetical order."""
    if by_size:
        sort_key = lambda dname: FSH.dir_size(os.path.join(rpath, dname))
    elif by_date:
        sort_key = lambda dname: os.path.getmtime(os.path.join(rpath, dname))
    else:
        sort_key = lambda dname: dname.lower()
    return sorted(dnames, key=sort_key, reverse=descending)
