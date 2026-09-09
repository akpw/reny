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


def test_git_status_propagation_to_parents():
    args = {
        'dir': '.',
        'git': True,
        'git_only': True,
        'end_level': 100,
        'include_dirs': True,
        'all_dirs': True,
        'all_files': True
    }
    params = FSEntryParamsBase(args)

    def mock_subprocess_run(cmd, *args, **kwargs):
        mock = MagicMock()
        mock.returncode = 0
        if 'rev-parse' in cmd:
            mock.stdout = '/mock/repo/root\n'
        elif 'status' in cmd:
            mock.stdout = ' M sub/nested/file.txt\n R old.txt -> new_sub/renamed.txt\n'
        else:
            mock.stdout = ''
        return mock

    with patch('subprocess.run', side_effect=mock_subprocess_run):
        params._init_git()

    # Leaf files
    assert params.git_statuses.get('/mock/repo/root/sub/nested/file.txt') == ' M'
    assert params.git_statuses.get('/mock/repo/root/new_sub/renamed.txt') == ' R'

    # Parent directories bubbled up with '* '
    assert params.git_statuses.get('/mock/repo/root/sub/nested') == '* '
    assert params.git_statuses.get('/mock/repo/root/sub') == '* '
    assert params.git_statuses.get('/mock/repo/root/new_sub') == '* '

    # Git root itself should not have '* '
    assert params.git_statuses.get('/mock/repo/root') is None

    # git_only filters: files and enclosing parent directories pass
    assert params.passed_git_filters('/mock/repo/root/sub/nested/file.txt', is_dir=False)
    assert params.passed_git_filters('/mock/repo/root/sub/nested', is_dir=True)
    assert params.passed_git_filters('/mock/repo/root/sub', is_dir=True)

    # Unrelated directory does not pass git_only
    assert not params.passed_git_filters('/mock/repo/root/unrelated_dir', is_dir=True)
    assert not params.passed_git_filters('/mock/repo/root/unrelated_dir/file.txt', is_dir=False)


