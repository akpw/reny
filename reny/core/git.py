# coding=utf8
"""
Reny Core Git: Decoupled Git repository status inspection and filter provider.
"""
import os
import subprocess
from typing import Dict, Set, Optional


class GitStatusTracker:
    """Manages Git repository discovery, porcelain status parsing, and status propagation."""

    def __init__(self, src_dir: Optional[str] = None):
        self.src_dir = os.path.realpath(src_dir) if src_dir else None
        self.is_git_repo = False
        self.git_root = ""
        self.git_statuses: Dict[str, str] = {}
        self.git_tracked_files: Set[str] = set()
        self.git_tracked_dirs: Set[str] = set()
        self.not_git_tracked_files: Set[str] = set()
        self.not_git_tracked_dirs: Set[str] = set()
        self.strictly_not_git_tracked_dirs: Set[str] = set()
        self.git_ignored_files: Set[str] = set()
        self.git_ignored_dirs: Set[str] = set()
        self.strictly_git_ignored_dirs: Set[str] = set()
        self._initialized = False

    def init(self, git: bool = True, git_only: bool = False,
             git_tracked: bool = False, not_git_tracked: bool = False,
             git_ignored: bool = False) -> None:
        """Discovers git root and populates cached porcelain statuses and trie-like sets."""
        if self._initialized:
            return
        self._initialized = True

        if not self.src_dir or (not git and not (git_only or git_tracked or not_git_tracked or git_ignored)):
            return

        try:
            res = subprocess.run(
                ['git', '-C', self.src_dir, 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True
            )
            if res.returncode != 0:
                if git_only or git_tracked or not_git_tracked or git_ignored:
                    print('Warning: Not a git repository')
                return

            self.is_git_repo = True
            self.git_root = res.stdout.strip()

            # 1. Porcelain statuses & parent directory propagation
            if git or git_only:
                res_status = subprocess.run(
                    ['git', '-C', self.src_dir, 'status', '--porcelain'],
                    capture_output=True, text=True
                )
                for line in res_status.stdout.splitlines():
                    if len(line) > 3:
                        status_code = line[:2]
                        rel_path = line[3:].strip('"')
                        if ' -> ' in rel_path:
                            rel_path = rel_path.split(' -> ')[-1].strip('"')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.git_statuses[full_path] = status_code

                        # Propagate bubble-up status to parent directories
                        parent_dir = os.path.dirname(full_path)
                        git_root_lower = os.path.normpath(self.git_root).lower()
                        while parent_dir and parent_dir != git_root_lower and parent_dir != '/':
                            if parent_dir not in self.git_statuses:
                                self.git_statuses[parent_dir] = '* '
                            parent_dir = os.path.dirname(parent_dir)

            # 2. Tracked files and parent directories
            if git_tracked:
                res_tracked = subprocess.run(
                    ['git', '-C', self.src_dir, 'ls-files', '--full-name'],
                    capture_output=True, text=True
                )
                git_root_lower = os.path.normpath(self.git_root).lower()
                for line in res_tracked.stdout.splitlines():
                    if line:
                        rel_path = line.strip('"')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.git_tracked_files.add(full_path)
                        parent_dir = os.path.dirname(full_path)
                        while parent_dir and parent_dir != git_root_lower and parent_dir != '/':
                            self.git_tracked_dirs.add(parent_dir)
                            parent_dir = os.path.dirname(parent_dir)

            # 3. Untracked files and directories
            if not_git_tracked:
                res_untracked = subprocess.run(
                    ['git', '-C', self.src_dir, 'ls-files', '--others', '--exclude-standard', '--full-name'],
                    capture_output=True, text=True
                )
                git_root_lower = os.path.normpath(self.git_root).lower()
                for line in res_untracked.stdout.splitlines():
                    if line:
                        rel_path = line.strip('"')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.not_git_tracked_files.add(full_path)
                        parent_dir = os.path.dirname(full_path)
                        while parent_dir and parent_dir != git_root_lower and parent_dir != '/':
                            self.not_git_tracked_dirs.add(parent_dir)
                            parent_dir = os.path.dirname(parent_dir)

                res_untracked_dirs = subprocess.run(
                    ['git', '-C', self.src_dir, 'ls-files', '--others', '--exclude-standard', '--directory', '--full-name'],
                    capture_output=True, text=True
                )
                for line in res_untracked_dirs.stdout.splitlines():
                    if line and line.endswith('/'):
                        rel_path = line.strip('"/')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.strictly_not_git_tracked_dirs.add(full_path)

            # 4. Ignored files and directories
            if git_ignored:
                res_ignored = subprocess.run(
                    ['git', '-C', self.src_dir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--full-name'],
                    capture_output=True, text=True
                )
                git_root_lower = os.path.normpath(self.git_root).lower()
                for line in res_ignored.stdout.splitlines():
                    if line:
                        rel_path = line.strip('"')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.git_ignored_files.add(full_path)
                        parent_dir = os.path.dirname(full_path)
                        while parent_dir and parent_dir != git_root_lower and parent_dir != '/':
                            self.git_ignored_dirs.add(parent_dir)
                            parent_dir = os.path.dirname(parent_dir)

                res_ignored_dirs = subprocess.run(
                    ['git', '-C', self.src_dir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--directory', '--full-name'],
                    capture_output=True, text=True
                )
                for line in res_ignored_dirs.stdout.splitlines():
                    if line and line.endswith('/'):
                        rel_path = line.strip('"/')
                        full_path = os.path.normpath(os.path.join(self.git_root, rel_path)).lower()
                        self.strictly_git_ignored_dirs.add(full_path)

        except Exception:
            if git_only or git_tracked or not_git_tracked or git_ignored:
                print('Warning: Not a git repository')

    def get_status(self, full_path: str) -> Optional[str]:
        """Returns direct git status letter (e.g. 'M ', '??', '* ') if tracked/modified."""
        return self.git_statuses.get(os.path.normpath(full_path).lower())

    def passed_filters(self, full_path: str, is_dir: bool = False, strictly_target: bool = False,
                       git_only: bool = False, git_tracked: bool = False,
                       not_git_tracked: bool = False, git_ignored: bool = False) -> bool:
        """Evaluates whether an entry meets git criteria."""
        full_path_lower = os.path.normpath(full_path).lower()

        if git_only:
            if full_path_lower not in self.git_statuses:
                return False

        if git_tracked:
            if is_dir:
                if full_path_lower not in self.git_tracked_dirs:
                    return False
            else:
                if full_path_lower not in self.git_tracked_files:
                    return False

        if not_git_tracked:
            if is_dir:
                if strictly_target:
                    if full_path_lower not in self.strictly_not_git_tracked_dirs:
                        return False
                else:
                    if full_path_lower not in self.not_git_tracked_dirs:
                        return False
            else:
                if full_path_lower not in self.not_git_tracked_files:
                    return False

        if git_ignored:
            if is_dir:
                if strictly_target:
                    if full_path_lower not in self.strictly_git_ignored_dirs:
                        return False
                else:
                    if full_path_lower not in self.git_ignored_dirs:
                        return False
            else:
                if full_path_lower not in self.git_ignored_files:
                    return False

        return True
