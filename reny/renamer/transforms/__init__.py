"""Pluggable file and directory rename transformation functions."""

from reny.renamer.transforms.index import DirCounters, build_index_transform
from reny.renamer.transforms.pad import build_pad_transform
from reny.renamer.transforms.date import build_date_transform
from reny.renamer.transforms.text import (
    build_add_text_transform,
    build_remove_n_chars_transform,
    build_capitalize_transform,
)
from reny.renamer.transforms.replace import build_replace_transform, expand_templates, substitute_dictionary

__all__ = [
    'DirCounters',
    'build_index_transform',
    'build_pad_transform',
    'build_date_transform',
    'build_add_text_transform',
    'build_remove_n_chars_transform',
    'build_capitalize_transform',
    'build_replace_transform',
    'expand_templates',
    'substitute_dictionary',
]
