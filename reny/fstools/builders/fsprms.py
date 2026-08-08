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


import os, sys, fnmatch, collections, pygtrie, heapq
import mimetypes
from enum import IntEnum
from abc import ABCMeta, abstractmethod
from reny.fstools.fsutils import FSH

from reny.fstools.builders.fsentry import FSEntryDefaults, FSMediaEntryType, FSMediaEntryGroupType
from reny.commons.descriptors import (
         PropertyDescriptor,
         LazyFunctionPropertyDescriptor,
         LazyClassPropertyDescriptor,
         FunctionPropertyDescriptor,
         BooleanPropertyDescriptor)

# FSEntry Attributes with default values
class FSEntryDefaultValueDescriptor(LazyFunctionPropertyDescriptor):
    pass

# FSEntry Attributes with default values
class FSEntryRuntimeAttributeDescriptor(PropertyDescriptor):
    pass


class FSEntryFilteredFilesValueDescriptor(FSEntryRuntimeAttributeDescriptor):
    ''' Files property descriptor
    '''
    def __set__(self, instance, value):
        if isinstance(instance, FSEntryParamsBase):
            # filtering
            if instance.filter_files:
                fnames = [fname for fname in value if instance.passed_filters(fname)]
            else:
                fnames = [fname for fname in value]

            # filter by git
            if instance.git:
                fnames = [fname for fname in fnames if instance.passed_git_filters(os.path.join(instance.rpath, fname), is_dir=False)]

            # file types
            if instance.file_type != FSMediaEntryGroupType.ANY:
                fnames = [fname for fname in fnames if instance.is_of_required_type(os.path.join(instance.rpath, fname))]

            # sorting
            if instance.by_size:
                sort_key = lambda fname: os.path.getsize(os.path.join(instance.rpath, fname))
            elif instance.by_date:
                sort_key = lambda fname: os.path.getmtime(os.path.join(instance.rpath, fname))
            else:
                sort_key = lambda fname: fname.lower()
            fnames.sort(key = sort_key, reverse = instance.descending)
            # set value
            super().__set__(instance, fnames)
        else:
            raise TypeError("Not a FSEntryParamsBase Type: {}".format(instance.__class__))


DNames = collections.namedtuple('DNames', ['passed', 'enclosing'])
class FSEntryFilteredDirsValueDescriptor(FSEntryRuntimeAttributeDescriptor):
    ''' Directories property descriptor
    '''
    def __set__(self, instance, value):
        if isinstance(instance, FSEntryParamsBase):
            passed_dnames, enclosing_dnames = [], []
            # filtering
            if instance.filter_dirs:
                for dname in value:
                    full_dname = os.path.join(instance.rpath, dname)
                    is_passed = False
                    if instance.file_type == FSMediaEntryGroupType.ANY and instance.passed_filters(dname):
                        if instance.passed_git_filters(full_dname, is_dir=True, strictly_target=True):
                            is_passed = True
                    
                    if is_passed:
                        passed_dnames.append(dname)
                    elif instance.scan_for_enclosing_directories:
                        en_dname = os.path.join(instance.rpath, dname)                        
                        if instance._enclosing_dnames.has_node(en_dname):
                            enclosing_dnames.append(dname)
            else:
                passed_dnames = [dname for dname in value]
            # sorting
            if instance.by_size:
               dirs_sort_key = lambda dname: FSH.dir_size(os.path.join(instance.rpath, dname))
            elif instance.by_date:
               dirs_sort_key = lambda dname: os.path.getmtime(os.path.join(instance.rpath, dname))
            else:
               dirs_sort_key = lambda dname: dname.lower()
            passed_dnames.sort(key = dirs_sort_key, reverse = instance.descending)
            enclosing_dnames.sort(key = dirs_sort_key, reverse = instance.descending)
            super().__set__(instance, DNames(passed_dnames, enclosing_dnames))
        else:
            raise TypeError("Not a FSEntryParamsBase Type: {}".format(instance.__class__))



class FSEntryRPathDescriptor(FSEntryRuntimeAttributeDescriptor):
    ''' RPath property descriptor
    '''
    def __set__(self, instance, value):
        if isinstance(instance, FSEntryParamsBase):
            super().__set__(instance, FSH.full_path(value))
        else:
            raise TypeError("Not a FSEntryParamsBase Type: {}".format(instance.__class__))


class FSEntryFileTypeDescriptor(PropertyDescriptor):
    ''' RPath property descriptor
    '''
    def __set__(self, instance, value):
        if isinstance(instance, FSEntryParamsBase):
            file_types_map =  {
              'image': FSMediaEntryType.IMAGE,
              'video': FSMediaEntryType.VIDEO,
              'audio': FSMediaEntryType.AUDIO,
              'nonmedia': FSMediaEntryType.NONMEDIA,
              'playable': FSMediaEntryGroupType.PLAYABLE,              
              'nonplayable': FSMediaEntryGroupType.NONPLAYABLE,                            
              'media': FSMediaEntryGroupType.MEDIA,
              'any': FSMediaEntryGroupType.ANY              
            }
            super().__set__(instance, file_types_map.get(value, FSMediaEntryGroupType.ANY))
        else:
            raise TypeError("Not a FSEntryParamsBase Type: {}".format(instance.__class__))



class FSEntryParamsBase():
    ''' Base Entry attributes
    '''
    src_dir = PropertyDescriptor()

    start_level = PropertyDescriptor()
    end_level = PropertyDescriptor()

    filter_dirs = BooleanPropertyDescriptor()
    filter_files = BooleanPropertyDescriptor()
    show_size = BooleanPropertyDescriptor()

    include = PropertyDescriptor()
    exclude = PropertyDescriptor()
    nested_indent = PropertyDescriptor()
    sort = PropertyDescriptor()
    file_type = FSEntryFileTypeDescriptor()
    # media_scan removed

    git = BooleanPropertyDescriptor()
    git_only = BooleanPropertyDescriptor()
    git_tracked = BooleanPropertyDescriptor()
    color = PropertyDescriptor()

    fs_entry_builder = LazyClassPropertyDescriptor('reny.fstools.builders.fsb.FSEntryBuilderBase')
    '''Runtime attrbutes
    '''
    rpath = FSEntryRPathDescriptor()
    fnames = FSEntryFilteredFilesValueDescriptor()
    dnames = FSEntryFilteredDirsValueDescriptor()
    
    def __init__(self, args = {}):
        self.src_dir = args.get('dir')
        self.start_level = args.get('start_level', 0)
        self.end_level = args.get('end_level', sys.maxsize)
        self.nested_indent = args.get('nested_indent', FSEntryDefaults.DEFAULT_NESTED_INDENT)
        self.include = args.get('include', FSEntryDefaults.DEFAULT_INCLUDE)
        self.exclude = args.get('exclude', FSEntryDefaults.DEFAULT_EXCLUDE)
        self.file_type = args.get('file_type', FSEntryDefaults.DEFAULT_FILE_TYPE)
        self.sort = args.get('sort', FSEntryDefaults.DEFAULT_SORT)
        self.filter_dirs = not args.get('all_dirs', False)
        self.filter_files = not args.get('all_files', False)   
        self.show_size = args.get('show_size', False)
        # fast_scan removed
        self.git = args.get('git', False)
        self.git_only = args.get('git_only', False)
        self.git_tracked = args.get('git_tracked', False)
        self.not_git_tracked = args.get('not_git_tracked', False)
        self.git_ignored = args.get('git_ignored', False)
        
        self.git_statuses = {}
        self.git_tracked_files = set()
        self.git_tracked_dirs = set()
        self.not_git_tracked_files = set()
        self.not_git_tracked_dirs = set()
        self.strictly_not_git_tracked_dirs = set()
        self.git_ignored_files = set()
        self.git_ignored_dirs = set()
        self.strictly_git_ignored_dirs = set()
        self._git_initialized = False

        if self.git_only or self.git_tracked or self.not_git_tracked or self.git_ignored:
            self.git = True
        self.color = args.get('color', 1)

        #self._media_extensions_cache = set()

        # enclosing directores
        self._enclosing_dnames = pygtrie.StringTrie(separator=os.path.sep)
        self._enclosing_files_containters = set()
        if self.scan_for_enclosing_directories:
            for rpath, dirs, files in os.walk(self.src_dir):
                # Prune ignored directories so we don't scan them
                dirs[:] = [d for d in dirs if not self.exclude_match(d)]
                
                if FSH.level_from_root(self.src_dir, rpath) < self.end_level:
                    marked_enclosing = False
                    for dir_name in dirs:
                        if self.file_type == FSMediaEntryGroupType.ANY and self.passed_filters(dir_name):
                            self._enclosing_dnames[rpath] = rpath
                            marked_enclosing = True
                            break # no need to check this root further
                    for file_name in files:
                        if self.passed_filters(file_name) and self.is_of_required_type(os.path.join(rpath,file_name)):
                            if self.git and not self.passed_git_filters(os.path.join(rpath,file_name), is_dir=False):
                                continue
                            if not marked_enclosing:
                                self._enclosing_dnames[rpath] = rpath
                            self._enclosing_files_containters.add(rpath)
                            break # no need to check this root further
            #print(self.file_type)
            #print('Enclosing: {}'.format(self._enclosing_dnames))
            #print('Enclosing File Containers: {}'.format(self._enclosing_files_containters))

    def _init_git(self):
        if self._git_initialized:
            return
        self._git_initialized = True

        if not self.git:
            return

        import subprocess
        try:
            res = subprocess.run(['git', '-C', self.src_dir, 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
            if res.returncode == 0:
                git_root = res.stdout.strip()
                if self.git or self.git_only:
                    res_status = subprocess.run(['git', '-C', self.src_dir, 'status', '--porcelain'], capture_output=True, text=True)
                    for line in res_status.stdout.splitlines():
                        if len(line) > 3:
                            status_code = line[:2]
                            rel_path = line[3:].strip('"')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.git_statuses[full_path] = status_code

                if self.git_tracked:
                    res_tracked = subprocess.run(['git', '-C', self.src_dir, 'ls-files', '--full-name'], capture_output=True, text=True)
                    for line in res_tracked.stdout.splitlines():
                        if line:
                            rel_path = line.strip('"')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.git_tracked_files.add(full_path)
                            parent_dir = os.path.dirname(full_path)
                            while parent_dir and parent_dir != os.path.normpath(git_root).lower() and parent_dir != '/':
                                self.git_tracked_dirs.add(parent_dir)
                                parent_dir = os.path.dirname(parent_dir)

                if self.not_git_tracked:
                    res_untracked = subprocess.run(['git', '-C', self.src_dir, 'ls-files', '--others', '--exclude-standard', '--full-name'], capture_output=True, text=True)
                    for line in res_untracked.stdout.splitlines():
                        if line:
                            rel_path = line.strip('"')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.not_git_tracked_files.add(full_path)
                            parent_dir = os.path.dirname(full_path)
                            while parent_dir and parent_dir != os.path.normpath(git_root).lower() and parent_dir != '/':
                                self.not_git_tracked_dirs.add(parent_dir)
                                parent_dir = os.path.dirname(parent_dir)
                    
                    res_untracked_dirs = subprocess.run(['git', '-C', self.src_dir, 'ls-files', '--others', '--exclude-standard', '--directory', '--full-name'], capture_output=True, text=True)
                    for line in res_untracked_dirs.stdout.splitlines():
                        if line and line.endswith('/'):
                            rel_path = line.strip('"/')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.strictly_not_git_tracked_dirs.add(full_path)


                if self.git_ignored:
                    res_ignored = subprocess.run(['git', '-C', self.src_dir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--full-name'], capture_output=True, text=True)
                    for line in res_ignored.stdout.splitlines():
                        if line:
                            rel_path = line.strip('"')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.git_ignored_files.add(full_path)
                            parent_dir = os.path.dirname(full_path)
                            while parent_dir and parent_dir != os.path.normpath(git_root).lower() and parent_dir != '/':
                                self.git_ignored_dirs.add(parent_dir)
                                parent_dir = os.path.dirname(parent_dir)

                    res_ignored_dirs = subprocess.run(['git', '-C', self.src_dir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--directory', '--full-name'], capture_output=True, text=True)
                    for line in res_ignored_dirs.stdout.splitlines():
                        if line and line.endswith('/'):
                            rel_path = line.strip('"/')
                            full_path = os.path.normpath(os.path.join(git_root, rel_path)).lower()
                            self.strictly_git_ignored_dirs.add(full_path)

            else:
                if self.git_only or self.git_tracked or self.not_git_tracked or self.git_ignored:
                    print('Warning: Not a git repository')

        except Exception:
            if self.git_only or self.git_tracked or self.not_git_tracked or self.git_ignored:
                print('Warning: Not a git repository')

    def passed_git_filters(self, full_path, is_dir=False, strictly_target=False):
        self._init_git()
        if not self.git:
            return True
        full_path_lower = os.path.normpath(full_path).lower()
        if self.git_only and not is_dir:
            if full_path_lower not in self.git_statuses:
                return False
        if self.git_tracked:
            if is_dir:
                if full_path_lower not in self.git_tracked_dirs:
                    return False
            else:
                if full_path_lower not in self.git_tracked_files:
                    return False
        if self.not_git_tracked:
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
        if self.git_ignored:
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

    # Current level
    @property
    def current_level(self):
        return FSH.level_from_root(self.src_dir, self.rpath)        

    # Sorting
    @property
    def descending(self):
        return True if self.sort.endswith('d') else False

    @property
    def by_size(self):
        return True if self.sort.startswith('s') else False

    @property
    def by_date(self):
        return True if self.sort.startswith('d') else False

    # Filtering
    @property
    def include_match(self):
        def match(fsname):
            for include_pattern in self.include.split(';'):
                if fnmatch.fnmatch(fsname, include_pattern):
                    return True
            return False
        return match

    @property
    def exclude_match(self):
        def match(fsname):
            for exclude_pattern in self.exclude.split(';'):
                if fnmatch.fnmatch(fsname, exclude_pattern):
                    return True
            return False
        return match

    @property
    def passed_filters(self):
        return lambda fs_name: self.include_match(fs_name) and (not self.exclude_match(fs_name))

    def is_of_entry_type(self, media_type):
        return {
          FSMediaEntryGroupType.ANY: True,
          FSMediaEntryType.IMAGE: media_type == FSMediaEntryType.IMAGE,
          FSMediaEntryType.VIDEO: media_type == FSMediaEntryType.VIDEO,          
          FSMediaEntryType.AUDIO: media_type == FSMediaEntryType.AUDIO,                    
          FSMediaEntryGroupType.PLAYABLE: media_type in (FSMediaEntryType.VIDEO, FSMediaEntryType.AUDIO),                    
          FSMediaEntryGroupType.NONPLAYABLE: media_type not in (FSMediaEntryType.VIDEO, FSMediaEntryType.AUDIO),                              
          FSMediaEntryGroupType.MEDIA: media_type in (FSMediaEntryType.IMAGE, FSMediaEntryType.VIDEO, FSMediaEntryType.AUDIO),                    
          FSMediaEntryType.NONMEDIA: media_type not in (FSMediaEntryType.IMAGE, FSMediaEntryType.VIDEO, FSMediaEntryType.AUDIO)
        }[self.file_type]


    def is_of_required_type(self, fpath):
        if self.file_type == FSMediaEntryGroupType.ANY:
            return True
            
        mime_type, _ = mimetypes.guess_type(fpath)
        media_type = FSMediaEntryType.NONMEDIA
        
        if mime_type:
            if mime_type.startswith('image/'):
                media_type = FSMediaEntryType.IMAGE
            elif mime_type.startswith('video/'):
                media_type = FSMediaEntryType.VIDEO
            elif mime_type.startswith('audio/'):
                media_type = FSMediaEntryType.AUDIO
                
        # Handle common extensions that mimetypes might miss on some systems
        if media_type == FSMediaEntryType.NONMEDIA:
            ext = os.path.splitext(fpath)[1].lower()
            if ext in ('.mkv', '.webm', '.avi', '.mp4'):
                media_type = FSMediaEntryType.VIDEO
            elif ext in ('.webp', '.png', '.jpg', '.jpeg', '.gif'):
                media_type = FSMediaEntryType.IMAGE
            elif ext in ('.flac', '.m4a', '.mp3', '.wav'):
                media_type = FSMediaEntryType.AUDIO

        return self.is_of_entry_type(media_type)

    @property
    def scan_for_enclosing_directories(self):
        return self.filter_dirs and (self.file_type != FSMediaEntryGroupType.ANY or self.include != FSEntryDefaults.DEFAULT_INCLUDE or getattr(self, 'git_ignored', False) or getattr(self, 'git_tracked', False) or getattr(self, 'not_git_tracked', False) or getattr(self, 'git_only', False)) and self.end_level > 0    

    @property
    def skip_iteration(self):   
        return True if (self.current_level < self.start_level) or (self.current_level > self.end_level) else False

    @property
    def end_iteration(self):
        return True if self.current_level > self.end_level else False

    @property
    def current_indent(self):
        return '{0}{1}'.format(self.nested_indent * (self.current_level), '|-> ' if not (self.isEnclosingEntry) else '|.. ')

    @property
    def siblings_indent(self):
        return '{0}{1}'.format(self.nested_indent * (self.current_level + 1), '|- ')

    @property
    def merged_dnames(self):
        return list(heapq.merge(self.dnames.passed, self.dnames.enclosing, reverse = self.descending))

    @property
    def isEnclosingEntry(self):
        return self._enclosing_dnames.has_node(self.rpath) and not self.isMatchingDirEntry

    @property
    def isMatchingDirEntry(self):
        dir_name = os.path.basename(self.rpath)
        if not (self.file_type == FSMediaEntryGroupType.ANY and self.passed_filters(dir_name)):
            return False
        return self.passed_git_filters(self.rpath, is_dir=True, strictly_target=True)
    
    @property
    def isEnclosingFilesContainterEntry(self):
        return self.rpath in self._enclosing_files_containters

    @property
    def args(self):
        return self._args
    
    @classmethod
    def writable_fields(cls):
        ''' generates names of all writable tag fields
        '''
        for c in cls.__mro__:
            for field, descr in vars(c).items():
                if isinstance(descr, LazyClassPropertyDescriptor):
                    continue
                if isinstance(descr, BooleanPropertyDescriptor):
                    yield field
                elif isinstance(descr, PropertyDescriptor):
                    yield field
    
    @classmethod
    def runtime_attributes(cls):
        ''' generates names of all runtime fields
        '''
        for c in cls.__mro__:
            for field, descr in vars(c).items():
                if isinstance(descr, FSEntryRuntimeAttributeDescriptor):
                    yield field

    # Copy attributes from another entry
    def copy_params(self, fs_entry_params):
        self._enclosing_dnames = fs_entry_params._enclosing_dnames
        self._enclosing_files_containters = fs_entry_params._enclosing_files_containters
        for field in self.writable_fields():
            value = getattr(fs_entry_params, field)
            if value is not None:
                setattr(self, field, value)

    def reset_runtime(self):
        for field in self.runtime_attributes():
            setattr(self, field, [])

    def __str__(self):
        return ('Entry of type: {}\n'.format(self.__class__.__name__) + \
            '\n '.join('{}: {}'.format(key, value) for key, value in vars(self).items()))  



class FSEntryParamsExt(FSEntryParamsBase):
    display_current = BooleanPropertyDescriptor()
    include_dirs = BooleanPropertyDescriptor()
    include_files = BooleanPropertyDescriptor()
    quiet = BooleanPropertyDescriptor()

    def __init__(self, args = {}):
        super().__init__(args)
        self.display_current = args.get('display_current', False)
        self.include_dirs = args.get('include_dirs', False)
        self.include_files = not args.get('exclude_files', False)
        self.quiet = args.get('quiet', False)       

    
class FSEntryParamsFlatten(FSEntryParamsExt):
    ''' Flatten Entry attributes
    '''
    fs_entry_builder = LazyClassPropertyDescriptor('reny.fstools.builders.fsb.FSEntryBuilderFlatten')
    
    target_level = PropertyDescriptor()
    remove_folders = BooleanPropertyDescriptor()
    remove_non_empty_folders = BooleanPropertyDescriptor()
    unique_fnames = FunctionPropertyDescriptor()
    non_empty_folders_mgs = PropertyDescriptor

    def __init__(self, args = {}):
        super().__init__(args)
        self.remove_folders = False if args.get('discard_flattened') == 'le' else True
        self.remove_non_empty_folders = True if args.get('discard_flattened') == 'da' else False
        self.unique_fnames = args.get('unique_fnames', FSH.unique_fnames)

        self.non_empty_folders_mgs = 'Use --discard-flattened parameter to remove non empty folders'

        self.target_level = args.get('target_level', 0)
        if self.end_level < self.target_level:
            self.end_level = self.target_level        



class FSEntryParamsOrganize(FSEntryParamsExt):
    ''' Organize Entry attributes
    '''
    fs_entry_builder = LazyClassPropertyDescriptor('reny.fstools.builders.fsb.FSEntryBuilderOrganizeWorker')

    by = PropertyDescriptor()
    date_format = PropertyDescriptor()
    target_dir = PropertyDescriptor()

    def __init__(self, args = {}):
        super().__init__(args)
        self.by = args.get('by')
        self.date_format = args.get('date_format')
        self.target_dir = args.get('target_dir')
