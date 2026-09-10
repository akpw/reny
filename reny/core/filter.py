# coding=utf8
"""
Reny Core Filter: Pattern matching and filtering utilities.
"""
import fnmatch
from typing import List, Callable, Optional


def glob_match(name: str, pattern_str: str) -> bool:
    """Matches a filename against a semicolon-separated list of glob patterns."""
    if not pattern_str:
        return False
    for pattern in pattern_str.split(';'):
        if pattern and fnmatch.fnmatch(name, pattern):
            return True
    return False


def passes_glob_patterns(
    name: str,
    include_patterns: str = "*",
    exclude_patterns: str = ".*"
) -> bool:
    """Evaluates whether name passes include and exclude pattern sets."""
    return glob_match(name, include_patterns) and not glob_match(name, exclude_patterns)
