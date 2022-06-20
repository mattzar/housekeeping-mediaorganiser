
from __future__ import annotations
import abc
from typing import Optional, List
from tools_utilities import find_files_on_removable_drives, list_filepaths_in_dir
import re

class FileSearch(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def find_files(self, extensions=None, directory: Optional[str]=None) -> FileSearch:
        ...

    def exclude_files(self, exclusions: List[str]) -> FileSearch:
        self.filepaths = [i for i in self.filepaths if not (any(re.compile(ex).search(str(i)) for ex in exclusions))]
        return self

    @property
    def filenames(self) -> List[str]:
        return [filepath.name for filepath in self.filepaths]

    def __len__(self) -> int:
        return len(self.filepaths)


class DirectorySearch(FileSearch):

    def find_files(self, extensions: List[str], directory: str) -> DirectorySearch:
        self.filepaths = list_filepaths_in_dir(directory, extensions)
        return self

class RemovableDriveSearch(FileSearch):

    def find_files(self, extensions: List[str]) -> RemovableDriveSearch:
        self.filepaths =  find_files_on_removable_drives(extensions)
        return self
        


