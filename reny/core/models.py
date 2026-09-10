# coding=utf8
"""
Reny Core Models: Typed dataclasses and enumerations.
"""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Optional, Tuple, Set, Dict, Any, List
import sys
import os

from reny.fstools.builders.fsentry import (
    FSEntry,
    FSEntryType,
    FSMediaEntryType,
    FSMediaEntryGroupType,
    FSEntryDefaults
)


class SortOrder(str, Enum):
    NAME_ASC = 'na'
    NAME_DESC = 'nd'
    SIZE_ASC = 'sa'
    SIZE_DESC = 'sd'
    DATE_ASC = 'da'
    DATE_DESC = 'dd'


@dataclass(frozen=True)
class ScanOptions:
    """Immutable user configuration and scan criteria for directory traversal."""
    src_dir: str = os.curdir
    src_file: Optional[str] = None
    recursive: bool = False
    start_level: int = 0
    end_level: int = sys.maxsize
    nested_indent: str = FSEntryDefaults.DEFAULT_NESTED_INDENT
    include: str = FSEntryDefaults.DEFAULT_INCLUDE
    exclude: str = FSEntryDefaults.DEFAULT_EXCLUDE
    ignore_file: Optional[str] = None
    filter_dirs: bool = True
    filter_files: bool = True
    file_type: str = FSEntryDefaults.DEFAULT_FILE_TYPE
    sort: str = FSEntryDefaults.DEFAULT_SORT
    show_size: bool = False
    color: int = 1
    quiet: bool = False
    git: bool = False
    git_only: bool = False
    git_tracked: bool = False
    not_git_tracked: bool = False
    git_ignored: bool = False
    by: Optional[str] = None
    date_format: str = '%Y-%m-%d'

    @property
    def descending(self) -> bool:
        return self.sort.endswith('d')

    @property
    def by_size(self) -> bool:
        return self.sort.startswith('s')

    @property
    def by_date(self) -> bool:
        return self.sort.startswith('d')


@dataclass
class RenamePlanItem:
    """Single proposed rename operation."""
    source_path: str
    target_path: str
    is_dir: bool
    status: str = "PENDING"  # PENDING, APPLIED, SKIPPED, ERROR
    error_message: Optional[str] = None
