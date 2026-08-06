import os
import io
import sys
from unittest.mock import patch, MagicMock

from reny.fstools.dirtools import DHandler
from reny.fstools.builders.fsprms import FSEntryParamsBase

def test_print_dir_git_only(mocker, tmp_path):
    # Setup args
    src_dir = str(tmp_path)
    args = {
        'dir': src_dir,
        'git_only': True,
        'git': True,
        'end_level': 2,
        'color': 0
    }
    params = FSEntryParamsBase(args)
    
    # Mock subprocess.run to simulate git output
    def mock_subprocess_run(cmd, *args, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        if "rev-parse" in cmd:
            mock_result.stdout = src_dir + "\n"
        elif "status" in cmd:
            mock_result.stdout = ' M child_dir/file_modified.txt\n?? child_dir/file_untracked.txt\n'
        return mock_result
        
    mocker.patch('subprocess.run', side_effect=mock_subprocess_run)
    
    # Mock DWalker.entries to simulate a directory structure
    from reny.fstools.builders.fsentry import FSEntryType, FSEntry
    
    child_dir = os.path.join(src_dir, "child_dir")
    dir_entry = FSEntry(FSEntryType.DIR, "child_dir", child_dir, "")
    dir_entry.isEnclosingEntry = False
    
    file_mod = FSEntry(FSEntryType.FILE, "file_modified.txt", os.path.join(child_dir, "file_modified.txt"), "  ")
    file_mod.isEnclosingEntry = False
    
    file_untrack = FSEntry(FSEntryType.FILE, "file_untracked.txt", os.path.join(child_dir, "file_untracked.txt"), "  ")
    file_untrack.isEnclosingEntry = False
    
    file_clean = FSEntry(FSEntryType.FILE, "file_clean.txt", os.path.join(child_dir, "file_clean.txt"), "  ")
    file_clean.isEnclosingEntry = False
    
    mocker.patch('reny.fstools.walker.DWalker.entries', return_value=[dir_entry, file_mod, file_untrack, file_clean])
    
    # Redirect stdout to capture print
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        DHandler.print_dir(params)
    finally:
        sys.stdout = sys.__stdout__
        
    output = captured_output.getvalue()
    
    # Assertions
    assert "[* ]" in output # dir_entry gets propagated asterisk
    assert "file_modified.txt [ M]" in output
    assert "file_untracked.txt [??]" in output
    assert "file_clean.txt" not in output # Should be filtered out by git_only
    
def test_print_dir_git_tracked(mocker, tmp_path):
    # Setup args
    src_dir = str(tmp_path)
    args = {
        'dir': src_dir,
        'git_tracked': True,
        'git': True,
        'end_level': 2,
        'color': 0
    }
    params = FSEntryParamsBase(args)
    
    # Mock subprocess.run to simulate git output
    def mock_subprocess_run(cmd, *args, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        if "rev-parse" in cmd:
            mock_result.stdout = src_dir + "\n"
        elif "status" in cmd:
            mock_result.stdout = ' M child_dir/file_modified.txt\n?? child_dir/file_untracked.txt\n'
        elif "ls-files" in cmd:
            mock_result.stdout = 'child_dir/file_modified.txt\nchild_dir/file_clean.txt\n'
        return mock_result
        
    mocker.patch('subprocess.run', side_effect=mock_subprocess_run)
    
    # Mock DWalker.entries to simulate a directory structure
    from reny.fstools.builders.fsentry import FSEntryType, FSEntry
    
    child_dir = os.path.join(src_dir, "child_dir")
    dir_entry = FSEntry(FSEntryType.DIR, "child_dir", child_dir, "")
    dir_entry.isEnclosingEntry = False
    
    file_mod = FSEntry(FSEntryType.FILE, "file_modified.txt", os.path.join(child_dir, "file_modified.txt"), "  ")
    file_mod.isEnclosingEntry = False
    
    file_untrack = FSEntry(FSEntryType.FILE, "file_untracked.txt", os.path.join(child_dir, "file_untracked.txt"), "  ")
    file_untrack.isEnclosingEntry = False
    
    file_clean = FSEntry(FSEntryType.FILE, "file_clean.txt", os.path.join(child_dir, "file_clean.txt"), "  ")
    file_clean.isEnclosingEntry = False
    
    mocker.patch('reny.fstools.walker.DWalker.entries', return_value=[dir_entry, file_mod, file_untrack, file_clean])
    
    # Redirect stdout to capture print
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        DHandler.print_dir(params)
    finally:
        sys.stdout = sys.__stdout__
        
    output = captured_output.getvalue()
    
    # Assertions
    assert "child_dir" in output
    assert "file_modified.txt" in output
    assert "file_clean.txt" in output # Should be included because it is tracked
    assert "file_untracked.txt" not in output # Should be filtered out by git_tracked
    # Check that counts reflect only the shown files
    # 2 files shown, 1 directory
    assert "2 files" in output
    assert "1 folder" in output

def test_print_dir_git_subdirectory(mocker, tmp_path):
    """Test that git statuses are correctly parsed when src_dir is a subdirectory of the git root."""
    git_root = str(tmp_path)
    src_dir = os.path.join(git_root, "sub_dir")
    os.makedirs(src_dir, exist_ok=True)
    
    args = {
        'dir': src_dir,
        'git': True,
        'git_only': False,
        'end_level': 2,
        'color': 0
    }
    params = FSEntryParamsBase(args)
    
    def mock_subprocess_run(cmd, *args, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        if "rev-parse" in cmd:
            mock_result.stdout = git_root + "\n"
        elif "status" in cmd:
            # git status ALWAYS returns paths relative to git_root
            mock_result.stdout = ' M sub_dir/file_modified.txt\n'
        return mock_result
        
    mocker.patch('subprocess.run', side_effect=mock_subprocess_run)
    
    from reny.fstools.builders.fsentry import FSEntryType, FSEntry
    
    file_mod = FSEntry(FSEntryType.FILE, "file_modified.txt", os.path.join(src_dir, "file_modified.txt"), "")
    file_mod.isEnclosingEntry = False
    
    mocker.patch('reny.fstools.walker.DWalker.entries', return_value=[file_mod])
    
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        DHandler.print_dir(params)
    finally:
        sys.stdout = sys.__stdout__
        
    output = captured_output.getvalue()
    
    # Assertions
    # If the bug was not fixed, it would look for sub_dir/sub_dir/file_modified.txt and fail to match
    assert "file_modified.txt [ M]" in output
