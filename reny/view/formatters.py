# coding=utf8
"""
Reny View Formatters: Formatting helpers for git status badges, file sizes, and summary lines.
"""
from typing import Optional
from reny.fstools.fsutils import FSH


def format_git_badge(status: Optional[str]) -> str:
    """Formats a git status indicator badge (e.g. ' [M ]', ' [??]')."""
    if status:
        return f" [{status}]"
    return ""


def format_size_badge(size_bytes: Optional[int]) -> str:
    """Formats a file or directory size badge (e.g. '  4KB ')."""
    if size_bytes is not None:
        return f" {FSH.fs_size(size_bytes)} "
    return ""


def format_summary(fcnt: int, dcnt: int, description: str = "file") -> str:
    """Formats entry count summary line."""
    files_part = f"{fcnt} {description}{'' if fcnt == 1 else 's'}"
    dirs_part = f"{dcnt} folder{'' if dcnt == 1 else 's'}"
    return f"{files_part}, {dirs_part}"


def format_total_size(total_size: int) -> str:
    """Formats cumulative size summary line."""
    return f"Total selected entries size: {FSH.fs_size(total_size)}"
