"""Text-based transformations: add text, remove characters, capitalization."""

import os
import string
from typing import Callable
from reny.fstools.builders.fsentry import FSEntry, FSEntryType


def build_add_text_transform(
    text: str,
    as_prefix: bool = False,
    join_str: str = ' ',
    include_dirs: bool = True,
    include_files: bool = True,
) -> Callable[[FSEntry], str]:
    """Builds a transformation callable that adds custom text as prefix or suffix."""
    addition = str(text)
    join_str = str(join_str)

    def add_text_transform(entry: FSEntry) -> str:
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

    return add_text_transform


def build_remove_n_chars_transform(
    num_chars: int = 0,
    from_head: bool = True,
    include_dirs: bool = True,
    include_files: bool = True,
) -> Callable[[FSEntry], str]:
    """Builds a transformation callable that strips N characters from the beginning or end of the filename base."""
    num_chars = abs(num_chars)

    def remove_n_chars_transform(entry: FSEntry) -> str:
        if entry.type == FSEntryType.ROOT:
            return entry.basename
        if entry.type == FSEntryType.DIR and not include_dirs:
            return entry.basename
        if entry.type == FSEntryType.FILE and not include_files:
            return entry.basename

        name_base, name_ext = os.path.splitext(entry.basename)
        if from_head:
            name_base = name_base[num_chars:]
        else:
            name_base = name_base[:-num_chars] if num_chars > 0 else name_base
        return f'{name_base}{name_ext}'

    return remove_n_chars_transform


def build_capitalize_transform(
    include_dirs: bool = True,
    include_files: bool = True,
) -> Callable[[FSEntry], str]:
    """Builds a transformation callable that capitalizes words in entry names."""
    def capitalize_transform(entry: FSEntry) -> str:
        if entry.type == FSEntryType.ROOT:
            return entry.basename
        if entry.type == FSEntryType.DIR and not include_dirs:
            return entry.basename
        if entry.type == FSEntryType.FILE and not include_files:
            return entry.basename

        return string.capwords(entry.basename)

    return capitalize_transform
