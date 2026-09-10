# coding=utf8
"""
Reny View Styler: ANSI terminal coloring based on entry type and file extensions.
"""
import os
from reny.fstools.builders.fsentry import FSEntryType

# Color definitions
COLOR_RESET = '\033[0m'
COLOR_DIR = '\033[1;34m'     # Bold Blue
COLOR_MEDIA = '\033[35m'   # Magenta
COLOR_DOCS = '\033[32m'    # Green
COLOR_ARCHIVE = '\033[31m' # Red
COLOR_TEXT = '\033[33m'    # Yellow
COLOR_CODE = '\033[36m'    # Cyan

EXT_MEDIA = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac', '.m4a'}
EXT_DOCS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods'}
EXT_ARCHIVE = {'.zip', '.tar', '.gz', '.7z', '.bz2', '.xz', '.rar'}
EXT_TEXT = {'.txt', '.md', '.conf', '.ini', '.json', '.yaml', '.yml', '.csv', '.log', '.toml'}
EXT_CODE = {'.py', '.js', '.ts', '.html', '.css', '.c', '.cpp', '.go', '.rs', '.java', '.sh', '.rb', '.php', '.sql'}


def style_entry(formatted_text: str, entry_type: int, filename: str = "", color_enabled: bool = True) -> str:
    """Applies ANSI terminal color formatting to directory or file entry names."""
    if not color_enabled:
        return formatted_text

    if entry_type == FSEntryType.DIR:
        return f"{COLOR_DIR}{formatted_text}{COLOR_RESET}"

    if entry_type == FSEntryType.FILE:
        name = filename or formatted_text
        ext = os.path.splitext(name)[1].lower()
        if ext in EXT_MEDIA:
            return f"{COLOR_MEDIA}{formatted_text}{COLOR_RESET}"
        elif ext in EXT_DOCS:
            return f"{COLOR_DOCS}{formatted_text}{COLOR_RESET}"
        elif ext in EXT_ARCHIVE:
            return f"{COLOR_ARCHIVE}{formatted_text}{COLOR_RESET}"
        elif ext in EXT_TEXT:
            return f"{COLOR_TEXT}{formatted_text}{COLOR_RESET}"
        elif ext in EXT_CODE:
            return f"{COLOR_CODE}{formatted_text}{COLOR_RESET}"

    return formatted_text
