"""Numeric indexing transformation."""

import os
from typing import Callable, Dict
from reny.fstools.builders.fsentry import FSEntry, FSEntryType
from reny.commons.utils import MiscHelpers


class DirCounters:
    """Directory entry counters helper for indexing."""
    def __init__(self, dirs_cnt: int = 0, files_cnt: int = 0, num_files: int = 0, num_dirs: int = 0):
        self.dirs_cnt = dirs_cnt
        self.files_cnt = files_cnt
        self.num_files = num_files
        self.num_dirs = num_dirs

    @staticmethod
    def num_digits(number: int, min_digits: int) -> int:
        return max(MiscHelpers.int_num_digits(number), min_digits)


def build_index_transform(
    fs_entry_params,
    total_files: int = 0,
    total_dirs: int = 0,
    as_prefix: bool = False,
    join_str: str = '_',
    start_from: int = 1,
    min_digits: int = 1,
    sequential: bool = False,
    by_directory: bool = False,
) -> Callable[[FSEntry], str]:
    """Constructs a stateful index formatting callable for batch renaming."""
    try:
        start_from = abs(int(start_from))
    except (ValueError, TypeError):
        start_from = 1

    counters: Dict[str, DirCounters] = {
        fs_entry_params.src_dir: DirCounters(start_from, start_from, 0, 0)
    }

    if sequential or by_directory:
        cnt_key = fs_entry_params.src_dir

        def index_sequential(entry: FSEntry) -> str:
            addition = None

            if entry.type == FSEntryType.DIR:
                if fs_entry_params.include_dirs:
                    addition = str(counters[cnt_key].dirs_cnt).zfill(DirCounters.num_digits(total_dirs, min_digits))
                if fs_entry_params.include_dirs or by_directory:
                    counters[cnt_key].dirs_cnt += 1

            elif entry.type == FSEntryType.FILE:
                if by_directory:
                    fcnt = counters[cnt_key].dirs_cnt - 1
                    if fcnt >= 0:
                        addition = str(fcnt).zfill(DirCounters.num_digits(total_files, min_digits))
                else:
                    addition = str(counters[cnt_key].files_cnt).zfill(DirCounters.num_digits(total_files, min_digits))
                    counters[cnt_key].files_cnt += 1

            return addition

        index_function = index_sequential
    else:
        def index_multilevel(entry: FSEntry) -> str:
            nonlocal total_files, total_dirs
            addition = None

            if entry.scopeSwitchingEntry:
                counters[entry.realpath] = DirCounters(
                    start_from, start_from,
                    len(fs_entry_params.fnames), len(fs_entry_params.dnames.passed)
                )

            cnt = counters[os.path.dirname(entry.realpath)]
            if entry.type == FSEntryType.DIR and fs_entry_params.include_dirs:
                addition = str(cnt.dirs_cnt).zfill(DirCounters.num_digits(cnt.num_dirs, min_digits))
                cnt.dirs_cnt += 1
                total_dirs += 1

            elif entry.type == FSEntryType.FILE:
                addition = str(cnt.files_cnt).zfill(DirCounters.num_digits(cnt.num_files, min_digits))
                cnt.files_cnt += 1
                total_files += 1

            return addition

        index_function = index_multilevel

    def add_index_transform(entry: FSEntry) -> str:
        addition = None

        if entry.type == FSEntryType.ROOT:
            pass
        elif entry.type == FSEntryType.DIR:
            addition = index_function(entry)
        elif entry.type == FSEntryType.FILE:
            if fs_entry_params.include_files:
                addition = index_function(entry)

        if addition is None:
            return entry.basename
        if as_prefix:
            return join_str.join((addition, entry.basename))
        else:
            name_base, name_ext = os.path.splitext(entry.basename)
            return f'{name_base}{join_str}{addition}{name_ext}'

    return add_index_transform
