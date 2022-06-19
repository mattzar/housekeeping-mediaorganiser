

import abc
from typing import Optional
from tools_utilities import find_files_on_removable_drives, list_filepaths_in_dir

class Seeker(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def find_files(self, extensions=None, directory: Optional[str] = None):
        ...

class DirectorySeeker(Seeker):

    def find_files(self, extensions, directory: Optional[str] = None):
        return list_filepaths_in_dir(directory, extensions)

class RemovableDriveSeeker(Seeker):

    def find_files(self, extensions, directory: Optional[str] = None):
        return find_files_on_removable_drives(extensions)
        


