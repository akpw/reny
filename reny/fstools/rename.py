# coding=utf8
## Copyright (c) 2014 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import os
from reny.fstools.dirtools import DHandler
from reny.fstools.builders.fsentry import FSEntryType
from reny.renamer.transforms import (
    DirCounters,
    build_index_transform,
    build_pad_transform,
    build_date_transform,
    build_add_text_transform,
    build_remove_n_chars_transform,
    build_capitalize_transform,
    build_replace_transform,
    expand_templates,
    substitute_dictionary,
)


class Renamer:
    """Renames FS entries applying pluggable transformations."""

    @classmethod
    def add_index(
        cls,
        fs_entry_params,
        as_prefix: bool = False,
        join_str: str = '_',
        start_from: int = 1,
        min_digits: int = 1,
        sequential: bool = False,
        by_directory: bool = False,
    ):
        """Adds indexing, automatically calculating appropriate digit padding."""
        total_files = total_dirs = 0
        if sequential or by_directory:
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)

        add_index_transform = build_index_transform(
            fs_entry_params,
            total_files=total_files,
            total_dirs=total_dirs,
            as_prefix=as_prefix,
            join_str=join_str,
            start_from=start_from,
            min_digits=min_digits,
            sequential=sequential,
            by_directory=by_directory,
        )

        if fs_entry_params.quiet:
            proceed = True
        else:
            proceed, _, _ = DHandler.visualise_changes(fs_entry_params, formatter=add_index_transform)

        if proceed:
            if (total_dirs + total_files) == 0:
                total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
            exec_transform = build_index_transform(
                fs_entry_params,
                total_files=total_files,
                total_dirs=total_dirs,
                as_prefix=as_prefix,
                join_str=join_str,
                start_from=start_from,
                min_digits=min_digits,
                sequential=sequential,
                by_directory=by_directory,
            )
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=exec_transform)

    @classmethod
    def pad(cls, fs_entry_params, min_digits: int):
        """Pads numbers in file and directory names with leading zeros."""
        pad_transform = build_pad_transform(
            min_digits,
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=pad_transform)

        if proceed:
            if (total_dirs + total_files) == 0:
                total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=pad_transform)

    @classmethod
    def capitalize(cls, fs_entry_params):
        """Capitalizes names of FS entries."""
        capitalize_transform = build_capitalize_transform(
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=capitalize_transform)

        if proceed:
            DHandler.rename_entries(
                fs_entry_params, total_files + total_dirs,
                formatter=capitalize_transform, check_unique=False
            )

    @classmethod
    def add_date(cls, fs_entry_params, as_prefix: bool = False, join_str: str = '_', format: str = '%Y-%m-%d'):
        """Adds current date prefix or suffix to entry names."""
        add_date_transform = build_date_transform(
            as_prefix=as_prefix,
            join_str=join_str,
            date_format=format,
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=add_date_transform)

        if proceed:
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=add_date_transform)

    @classmethod
    def add_text(cls, fs_entry_params, text: str, as_prefix: bool = False, join_str: str = ' '):
        """Adds arbitrary text as prefix or suffix."""
        add_text_transform = build_add_text_transform(
            text=text,
            as_prefix=as_prefix,
            join_str=join_str,
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=add_text_transform)

        if proceed:
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=add_text_transform)

    @classmethod
    def remove_n_characters(cls, fs_entry_params, num_chars: int = 0, from_head: bool = True):
        """Removes n characters from entry name head or tail."""
        remove_n_chars_transform = build_remove_n_chars_transform(
            num_chars=num_chars,
            from_head=from_head,
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=remove_n_chars_transform)

        if proceed:
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=remove_n_chars_transform)

    @classmethod
    def replace(cls, fs_entry_params, find_str: str, replace_str: str, case_insensitive: bool = False, include_extension: bool = False):
        """Regexp-based find and replace with template variable substitution."""
        replace_transform = build_replace_transform(
            find_str=find_str,
            replace_str=replace_str,
            case_insensitive=case_insensitive,
            include_extension=include_extension,
            include_dirs=fs_entry_params.include_dirs,
            include_files=fs_entry_params.include_files,
        )

        if fs_entry_params.quiet:
            proceed = True
            total_files, total_dirs, _ = DHandler.dir_stats(fs_entry_params)
        else:
            proceed, total_files, total_dirs = DHandler.visualise_changes(fs_entry_params, formatter=replace_transform)

        if proceed:
            DHandler.rename_entries(fs_entry_params, total_files + total_dirs, formatter=replace_transform)

    @classmethod
    def delete(cls, fs_entry_params):
        """Deletes selected entries."""
        if fs_entry_params.filter_dirs & fs_entry_params.include_dirs:
            fs_entry_params.filter_files = False
            fs_entry_params.include_files = True

        def delete_transform(entry):
            if entry.type == FSEntryType.ROOT:
                return entry.basename
            if entry.type == FSEntryType.DIR and not fs_entry_params.include_dirs:
                return None
            if entry.type == FSEntryType.FILE and not fs_entry_params.include_files:
                return None
            return entry.basename

        if fs_entry_params.quiet:
            proceed = True
        else:
            proceed, _, _ = DHandler.visualise_changes(
                fs_entry_params,
                formatter=delete_transform,
                after_msg='The following files / folders will be deleted'
            )

        if proceed:
            DHandler.remove_entries(fs_entry_params, formatter=delete_transform)

    @classmethod
    def organize(cls, fs_entry_params):
        """Organizes files by selected attributes."""
        print('to be organized')

    @classmethod
    def _expand_templates(cls, entry, value: str) -> str:
        """Expands template values for backward compatibility."""
        return expand_templates(entry, value)

    @classmethod
    def _substitute_dictionary(cls, entry) -> dict:
        """Internal template value substitution for backward compatibility."""
        return substitute_dictionary(entry)
