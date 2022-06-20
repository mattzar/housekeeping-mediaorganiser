from __future__ import annotations
import abc
import pathlib
from typing import overload
from tools_metadata import get_date_from_image_filename
import shutil
import logging
from typing import overload
from exceptions import CannotMoveFileError

class FileSorter(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def path(self, filename: str) -> pathlib.Path:
        ...

    @overload
    def sort(self, filepath: pathlib.Path, destination: pathlib.Path, method: str = "copy") -> None:
        ...

    def sort(self, filepath: str, destination: str, method: str = "copy") -> None:

        if ~isinstance(filepath, pathlib.Path):
            filepath = pathlib.Path(filepath)
        if ~isinstance(destination, pathlib.Path):
            destination = pathlib.Path(destination)

        destination_full = destination / self.path(filepath)
    
        try:
            self.make_dir(destination_full)

            if method == "move":
                relocate_method = self.move
                
            elif method == "copy":
                relocate_method = self.copy

            relocate_method(filepath, destination_full)

        except shutil.Error as e:
            logging.error(f"{filepath.name}: Cannot move file")
            raise CannotMoveFileError from e

    
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

    def path(self, filepath:pathlib.Path) -> str:
        return get_date_from_image_filename(filepath.name, "%Y-%m")


class ImageByLocationSorter(FileSorter):

    def path(self, filename: str) -> str:
        return 0

        # with geo.GoogleMapsClient() as client:
        # locations = client.aggregate_reverse_geocode(queue)


def main():
    pass

if __name__ == "__main__":
    main()