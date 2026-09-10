"""Regex-based find and replace transformation with string template substitution."""

import datetime
import os
import re
from string import Template
from typing import Callable, Optional
from reny.fstools.builders.fsentry import FSEntry, FSEntryType


def substitute_dictionary(entry: FSEntry) -> dict:
    """Builds interpolation dictionary for template variables from entry metadata."""
    sd = {}
    full_dir_name = os.path.dirname(entry.realpath)
    sd['dirname'] = os.path.basename(full_dir_name)
    sd['pardirname'] = os.path.basename(os.path.dirname(full_dir_name))

    sd['adtime'] = datetime.datetime.fromtimestamp(os.path.getatime(entry.realpath))
    sd['cdtime'] = datetime.datetime.fromtimestamp(os.path.getctime(entry.realpath))
    sd['mdtime'] = datetime.datetime.fromtimestamp(os.path.getmtime(entry.realpath))

    sd['atime'] = datetime.datetime.fromtimestamp(os.path.getatime(entry.realpath)).time()
    sd['ctime'] = datetime.datetime.fromtimestamp(os.path.getctime(entry.realpath)).time()
    sd['mtime'] = datetime.datetime.fromtimestamp(os.path.getmtime(entry.realpath)).time()

    sd['adate'] = datetime.datetime.fromtimestamp(os.path.getatime(entry.realpath)).date()
    sd['cdate'] = datetime.datetime.fromtimestamp(os.path.getctime(entry.realpath)).date()
    sd['mdate'] = datetime.datetime.fromtimestamp(os.path.getmtime(entry.realpath)).date()

    return sd


def expand_templates(entry: FSEntry, value: str) -> str:
    """Expands template variables ($dirname, $mdate, etc.) in replacement string."""
    template = Template(value)
    return template.safe_substitute(substitute_dictionary(entry))


def build_replace_transform(
    find_str: str,
    replace_str: Optional[str] = None,
    case_insensitive: bool = False,
    include_extension: bool = False,
    include_dirs: bool = True,
    include_files: bool = True,
) -> Callable[[FSEntry], str]:
    """Builds regex-based replacement transformation callable."""
    flags = re.UNICODE
    if case_insensitive:
        flags = flags | re.IGNORECASE
    p = re.compile(find_str, flags)

    def replace_transform(entry: FSEntry) -> str:
        if entry.type == FSEntryType.ROOT:
            return entry.basename
        if entry.type == FSEntryType.DIR and not include_dirs:
            return entry.basename
        if entry.type == FSEntryType.FILE and not include_files:
            return entry.basename

        name_base, name_ext = os.path.splitext(entry.basename)
        target_text = entry.basename if include_extension else name_base
        match = p.search(target_text)
        if match:
            if replace_str is not None:
                replace_str_expanded = expand_templates(entry, replace_str)
                res = p.sub(replace_str_expanded, target_text)
            else:
                res = match.group()
            return f"{res}{'' if include_extension else name_ext}"
        else:
            return entry.basename

    return replace_transform
