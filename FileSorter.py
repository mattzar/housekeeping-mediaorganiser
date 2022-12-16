from __future__ import annotations
import abc
from pathlib import Path
from PIL import UnidentifiedImageError
from tools_metadata import get_date_from_image_file, get_metadata_from_exif
import shutil
import logging
from exceptions import CannotMoveFileError
import os

class FileSorter(abc.ABC):

    # def __init__(self):
    #     pass

    @abc.abstractmethod
    def path(self, filename: Path) -> Path:
        ...

    def sort(self, filepath: Path, destination: Path, options:dict) -> None:

        subfolder: dict = options["subfolder"]
        method: str = options["method"] or "copy"
        min_file_size = options["min_file_size"] * (1024 * 1024) or 0

        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        if not isinstance(destination, Path):
            destination = Path(destination)

        destination_full = destination / self.path(filepath)

        if subfolder["enabled"]:
            try:
                metadata = get_metadata_from_exif(filepath)
                for field, value in subfolder["masked_fields"].items():
                    assert metadata[field] == value
            except (KeyError, AssertionError, UnidentifiedImageError):
                if os.stat(filepath).st_size >= min_file_size and filepath.suffix in [
                    ".mp4",
                    ".3gp",
                    ".MP4",
                    ".mov",
                ]:
                    logging.info(f"Subfolders are enabled, but {filepath.name} is a movie and above maximum specified file size, so moving to {destination_full}")
                else:
                    destination_full = destination_full / subfolder["subfolder_name"]
                logging.info(f"Subfolders are enabled, {filepath.name} not included in subfolder.masked_fields settings, moving to {destination_full}")
                
                    


        try:
            self.make_dir(destination_full)

            if method == "copy":
                relocate_method = self.copy

            elif method == "move":
                relocate_method = self.move

            relocate_method(filepath, destination_full)

        except shutil.Error as e:
            logging.error(f"{filepath.name}: Cannot move file")
            raise CannotMoveFileError from e

    def make_dir(self, path:Path) -> None:
        directory = path.parents[0] if path.is_file() else path
        directory.mkdir(parents=True, exist_ok=True)

    def move(self, filepath:Path, destination:Path) -> None:
        shutil.move(filepath, destination)
        logging.info(f"{filepath.name} moved to {destination.parents[0]}")

    def copy(self, filepath:Path, destination:Path) -> None:
        shutil.copy(filepath, destination)
        logging.info(f"{filepath.name} copied to {destination.parents[0]}")


class ImageByDateSorter(FileSorter):

    def __init__(self, input_format, output_format:str = None, *args, **kwargs):
        self.input_format = input_format or dict(regex=r"\d{8}", dateformat="%Y%m%d")
        self.ouput_format = output_format or "%Y-%m"
        super().__init__(*args, **kwargs)

    def path(self, filepath:Path) -> Path:
        return Path(get_date_from_image_file(filepath, format=self.input_format).strftime(self.ouput_format))


class ImageByLocationSorter(FileSorter):

    def path(self, filepath:Path) -> Path:
        return Path("")

        # with geo.GoogleMapsClient() as client:
        # locations = client.aggregate_reverse_geocode(queue)


def main():
    pass

if __name__ == "__main__":
    main()