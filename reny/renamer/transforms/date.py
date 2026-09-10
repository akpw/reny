"""Date prefix and suffix injection transformation."""

import datetime
import os
from typing import Callable
from reny.fstools.builders.fsentry import FSEntry, FSEntryType


def build_date_transform(
    as_prefix: bool = False,
    join_str: str = '_',
    date_format: str = '%Y-%m-%d',
    include_dirs: bool = True,
    include_files: bool = True,
) -> Callable[[FSEntry], str]:
    """Builds a transformation callable that adds the formatted current date to entry names."""
    addition = datetime.datetime.now().strftime(date_format)
    join_str = str(join_str)

    def add_date_transform(entry: FSEntry) -> str:
        if entry.type == FSEntryType.ROOT:
            return entry.basename
        if entry.type == FSEntryType.DIR and not include_dirs:
            return entry.basename
        if entry.type == FSEntryType.FILE and not include_files:
            return entry.basename

        if as_prefix:
            return join_str.join((addition, entry.basename))
        else:
            name_base, name_ext = os.path.splitext(entry.basename)
            return f'{name_base}{join_str}{addition}{name_ext}'

    return add_date_transform
