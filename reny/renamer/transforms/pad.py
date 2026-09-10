"""Number padding transformation with leading zeros."""

import re
from typing import Callable
from reny.fstools.builders.fsentry import FSEntry, FSEntryType


def build_pad_transform(min_digits: int, include_dirs: bool = True, include_files: bool = True) -> Callable[[FSEntry], str]:
    """Builds a transformation callable that pads the first number in the entry name with leading zeros."""
    def pad_match(m: re.Match) -> str:
        return m.group(0).zfill(min_digits)

    def pad_transform(entry: FSEntry) -> str:
        if entry.type == FSEntryType.ROOT:
            return entry.basename
        if entry.type == FSEntryType.DIR and not include_dirs:
            return entry.basename
        if entry.type == FSEntryType.FILE and not include_files:
            return entry.basename

        return re.sub(r'\d+', pad_match, entry.basename, count=1)

    return pad_transform
