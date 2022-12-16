from __future__ import annotations
from pathlib import Path
import logging
import sys
from LogFormatter import setup_logging
import argparse
import yaml
from ImageQueue import ImageQueue

from FileSorter import FileSorter, ImageByDateSorter, ImageByLocationSorter
from FileSearch import DirectorySearch, RemovableDriveSearch

from exceptions import CannotMoveFileError

class MediaSorter:
    def __init__(self, params:argparse.ArgumentParser = None):

        settings_path = Path(Path().absolute(), "settings.yaml")
        with open(settings_path, "r") as file:
            settings = yaml.safe_load(file)

        try:
            params_default = settings["defaults"] | settings["jobs"][params.job]
        except KeyError:
            params_default = settings["defaults"]

        params = params_default | {k: v for k, v in vars(params).items() if v is not None}

        self.input = Path(params["input"])
        self.output = Path(params["output"])
        self.log = Path(params["output"], params["log"])
        self.loglevel = params["loglevel"]
        self.extensions = params["extensions"]
        self.foldernames = params["foldernames"]
        self.method=params["method"]
        self.formats=params["formats"]
        self.subfolder= params["subfolder"]
        self.min_file_size=params["min_file_size"]

        try:
            self.exclusions = params["exclusions"].split(" ")
        except AttributeError:
            self.exclusions = params["exclusions"] if isinstance(params["exclusions"], list) else (params["exclusions"],)

        Path(self.output).mkdir(parents=True, exist_ok=True)

        # Setup logging
        if not setup_logging(
            console_log_output="stdout",
            console_log_level="info",
            console_log_color=True,
            logfile_file=self.log,
            logfile_log_level=self.loglevel,
            logfile_log_color=False,
            log_line_template="%(color_on)s[%(asctime)s] [%(threadName)s] [%(levelname)-8s] %(message)s%(color_off)s",
        ):
            print("Failed to setup logging, aborting.")
            exit()

    def process_job(self) -> None:

        logging.info("Starting job")

        # if input is set to removable drives, look for files of type self.extensions
        if self.input.name == "removables":
            input_files = RemovableDriveSearch() \
                .find_files(extensions=self.extensions) \
                .exclude_files(self.exclusions)
            logging.info(f"{len(input_files)} files found in on removable drives")
        # otherwise look for files in the defined input directory
        else:
            input_files = DirectorySearch() \
                .find_files(extensions=self.extensions, directory=self.input) \
                .exclude_files(self.exclusions)
            logging.info(f"{len(input_files)} files found in input folder: {self.input}")
        
        # Find all existing files in output directory with specified extensions
        existing_files = DirectorySearch() \
            .find_files(extensions=self.extensions, directory=self.output)
        logging.info(f"{len(existing_files)} files found in output folder: {self.output}")

        # Form queue of files of type in 'extensions', which are in input but not already in output (avoids copying files already present)
        q = ImageQueue([file for file in input_files.filepaths if file.name not in existing_files.filenames])
        logging.info(f"{q.qsize()} files added to job queue")

        sorter: FileSorter # Forward declaration to appease mypy linter
        if self.foldernames == "date":
            sorter = ImageByDateSorter(
                input_format = self.formats["input"],
                output_format=self.formats["output"]
            )
        elif self.foldernames == "location":
            sorter = ImageByLocationSorter()

        while not q.empty():

            image = q.get()

            logging.info(f"{str(q)} Sorting {image.name} from folder {image.parents[0]}")

            try:
                sorter.sort(
                    filepath=image,
                    destination=self.output,
                    options=dict(
                        method=self.method,
                        formats=self.formats,
                        subfolder= self.subfolder,
                        min_file_size=self.min_file_size
                    )
                )

            except CannotMoveFileError:
                sorter.sort(
                    filepath=image,
                    destination=self.output,
                    options=dict(
                        method="copy",
                        formats=self.formats,
                        subfolder= self.subfolder,
                        min_file_size=self.min_file_size
                    )
                )

        logging.info("Finished job")


def arg_handler() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="A program to sort media")
    parser.add_argument("-i", "--input", help="path to source directory")
    parser.add_argument("-o", "--output", help="path to output directory")
    parser.add_argument("-l", "--log", help="path to log output file")
    parser.add_argument("-e", "--extensions", help="filetypes to include in sort")
    parser.add_argument("-x", "--exclude", help="wildcarded names to exclude")
    parser.add_argument("-f", "--foldernames", help="wildcarded names to exclude")
    parser.add_argument("-m", "--method", help="select 'copy' or 'move' files")
    parser.add_argument("-j", "--job", help="select a preset job")
    parser.add_argument(
        "-v",
        "--loglevel",
        help="select log level critical | error | warning | info | debug",
    )

    return parser.parse_args()


def main():

    MediaSorter(params=arg_handler()).process_job()


if __name__ == "__main__":
    sys.exit(main())
