from __future__ import annotations
import abc
import pathlib
from typing import overload
from tools_metadata import get_date_from_image_filename
# import os
import shutil
import logging
from typing import overload

class FileSorter(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def path(self, filename: str) -> pathlib.Path:
        ...

    @overload
    def sort(self, filepath: pathlib.Path, destination: pathlib.Path, method: str="copy"):
        ...

    def sort(self, filepath: str, destination: str, method: str="copy"):

        if ~isinstance(filepath, pathlib.Path):
            filepath = pathlib.Path(filepath)
        if ~isinstance(destination, pathlib.Path):
            destination = pathlib.Path(destination)

        destination_full = destination / self.path(filepath) / filepath.name
    
        try:
            self.make_dir(destination_full)

            if method == "move":
                relocate_method = self.move()
                
            elif method == "copy":
                relocate_method = self.copy()

            relocate_method(filepath, destination_full)

        except shutil.Error:

            logging.info(f"{filepath.name}: Cannot move file, attempting to copy instead")
            shutil.copy(filepath, destination_full)
            logging.info(f"{filepath.name} copied to {destination_full.parents[0]}")

    
    def make_dir(self, path:pathlib.Path) -> None:
        directory = path.parents[0] if path.is_file() else path
        directory.mkdir(parents=True, exist_ok=True)

    def move(self, filepath:pathlib.Path, destination:pathlib.Path) -> None:
        shutil.move(filepath, destination)
        logging.info(f"{filepath.name} moved to {destination.parents[0]}")

    def copy(self, filepath:pathlib.Path, destination:pathlib.Path) -> None:
        shutil.copy(filepath, destination)
        logging.info(f"{filepath.name} copied to {destination.parents[0]}")


class ImageByDateSorter(FileSorter):

    def path(self, filename: str) -> str:
        return get_date_from_image_filename(filename, "%Y-%m")


class ImageByLocationSorter(FileSorter):

    def path(self, filename: str) -> str:
        return 0


def main():
    pass

if __name__ == "__main__":
    main()