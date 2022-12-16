from __future__ import annotations
from typing import List
from tools_utilities import find_files_on_removable_drives, list_filepaths_in_dir
import re
from pathlib import Path

class FileSearch:

    def __init__(self):
        self.filepaths: List[Path]

    def exclude_files(self, exclusions: List[str]) -> FileSearch:
        self.filepaths = [i for i in self.filepaths if not (any(re.compile(ex).search(str(i)) for ex in exclusions))]
        return self

    @property
    def filenames(self) -> List[str]:
        return [filepath.name for filepath in self.filepaths]

    def __len__(self) -> int:
        return len(self.filepaths)

    def __iter__(self) -> Path:
        yield from self.filepaths


class DirectorySearch(FileSearch):

    def find_files(self, extensions:List[str], directory:Path) -> DirectorySearch:
        self.filepaths = list_filepaths_in_dir(directory, extensions)
        return self

class RemovableDriveSearch(FileSearch):

    def find_files(self, extensions:List[str]) -> RemovableDriveSearch:
        self.filepaths =  find_files_on_removable_drives(extensions)
        return self
        


