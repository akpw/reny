import os
from unittest.mock import patch, MagicMock
from reny.fstools.builders.fsprms import FSEntryParamsBase

def test_git_ignored_filters_directories():
    args = {
        'dir': '.',
        'git_ignored': True,
        'end_level': 100,
        'include_dirs': True,
        'all_dirs': True,
        'all_files': True
    }
    params = FSEntryParamsBase(args)
    
    # Mock subprocess.run to simulate git output
    def mock_subprocess_run(cmd, *args, **kwargs):
        mock = MagicMock()
        mock.returncode = 0
        if 'rev-parse' in cmd:
            mock.stdout = '/mock/repo/root\n'
        elif 'ls-files' in cmd:
            if '--directory' in cmd:
                if '--ignored' in cmd:
                    # Git only yields fully ignored directories here, e.g. __pycache__/
                    mock.stdout = 'fully_ignored_dir/\n'
                else:
                    mock.stdout = ''
            else:
                if '--ignored' in cmd:
                    # Git yields specific ignored files here, including those inside mixed tracked/untracked directories
                    mock.stdout = 'fully_ignored_dir/file1.txt\nmixed_dir/ignored_file.txt\n'
                else:
                    mock.stdout = ''
        else:
            mock.stdout = ''
        return mock
    
    with patch('subprocess.run', side_effect=mock_subprocess_run):
        params._init_git()
        
    assert '/mock/repo/root/fully_ignored_dir' in params.strictly_git_ignored_dirs
    assert '/mock/repo/root/fully_ignored_dir' in params.git_ignored_dirs
    assert '/mock/repo/root/mixed_dir' in params.git_ignored_dirs # mixed_dir has an ignored file, so it's in the broader list
    
    # Test passed_git_filters for fully ignored directory
    assert params.passed_git_filters('/mock/repo/root/fully_ignored_dir', is_dir=True, strictly_target=True)
    
    # Test passed_git_filters for mixed directory (contains tracked files + ignored files)
    # strictly_target=True -> False (it won't be deleted)
    assert not params.passed_git_filters('/mock/repo/root/mixed_dir', is_dir=True, strictly_target=True)
    # strictly_target=False -> True (it acts as an enclosing directory for traversal)
    assert params.passed_git_filters('/mock/repo/root/mixed_dir', is_dir=True, strictly_target=False)
    
    # Test passed_git_filters for a completely untracked/unignored random directory
    assert not params.passed_git_filters('/mock/repo/root/random_dir', is_dir=True, strictly_target=True)
    
    # Test passed_git_filters for files
    assert params.passed_git_filters('/mock/repo/root/mixed_dir/ignored_file.txt', is_dir=False)

