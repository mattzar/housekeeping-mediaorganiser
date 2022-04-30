import os
import pathlib
import shutil
import re
import logging
import sys
from log_formatter import setup_logging
import argparse
import psutil

import yaml
import tools_utilities as util
import tools_metadata as meta
import media_geocoder as geo


class MediaSorter:
    def __init__(self, params=None):

        with open("settings.yaml", "r") as file:
            settings = yaml.safe_load(file)

        self.input = pathlib.Path(params.input or settings["defaults"]["input"])
        self.output = pathlib.Path(params.output or settings["defaults"]["output"])
        self.log = pathlib.Path(
            params.log or settings["defaults"]["output"] + settings["defaults"]["log"]
        )
        self.loglevel = params.loglevel or settings["defaults"]["loglevel"]
        self.extensions = params.include or tuple(settings["defaults"]["extensions"])
        self.foldernames = params.foldernames or settings["defaults"]["foldernames"]
        self.method = settings["defaults"]["method"]

        try:
            self.exclusions = params.exclude.split(" ")
        except AttributeError:
            self.exclusions = settings["defaults"]["exclusions"]

    def process_job(self):

        # os.makedirs(os.path.dirname(self.output), exist_ok=True)
        pathlib.Path(self.output).mkdir(parents=True, exist_ok=True)

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
            return 1

        logging.info("Starting job")

        if self.input.name == "removables":

            input_files = []
            logging.info(
                f"Searching for files of type {self.extensions} on removable drives"
            )

            # Find all removable partitions
            removable_drives = [
                part
                for part in psutil.disk_partitions()
                if "removable" in part.opts.split(",")
            ]
            logging.info(f"{len(removable_drives)} removable drives found")

            for drive in removable_drives:
                input_files += util.list_filepaths_in_dir(
                    drive.mountpoint, self.extensions
                )
        else:
            input_files = util.list_filepaths_in_dir(self.input, self.extensions)

        # Exclude files that start with '.'
        input_files = [
            el for el in input_files if not os.path.basename(el).startswith(".")
        ]
        # Walk through input dir, return files of type in 'extensions'
        existing = [
            os.path.basename(el)
            for el in util.list_filepaths_in_dir(self.output, self.extensions)
        ]
        # Form queue of files of type in 'extensions', which are in input but not already in output (avoids duplicates)
        queue = [el for el in input_files if os.path.basename(el) not in existing]

        # remove any exluded files
        regex = [re.compile(ex) for ex in self.exclusions]
        queue = [i for i in queue if not (any(ex.search(i) for ex in regex))]

        logging.info(f"{len(input_files)} files found in input folder: {self.input}")
        logging.info(f"{len(existing)} files found in output folder: {self.output}")
        logging.info(f"{len(queue)} files added to job queue")

        if self.foldernames == "location":
            locations = geo.aggregate_reverse_geocode(queue)

        while queue:

            image = queue.pop()

            if self.foldernames == "date":
                folder, message = meta.get_date_from_image_filename(image, "%Y-%m")

            elif self.foldernames == "location":
                folder, message = locations[0]

            logging.info(message)

            try:
                # pathlib.Path(self.output / folder).mkdir(parents=True, exist_ok=True)

                if self.method == "move":
                    shutil.move(image, self.output / folder)
                    logging.info(f"{image} moved to {self.output / folder}")

                elif self.method == "copy":
                    shutil.copy(image, self.output / folder)
                    logging.info(f"{image} copied to {self.output / folder}")

            except PermissionError:
                queue.insert(0, image)
                logging.info(
                    "f{image} is currently not available, sending to back of queue and continuing"
                )

            except shutil.Error:
                logging.info(f"{image}: Cannot move file, copying instead")
                shutil.copy(image, self.output / folder)

        logging.info("Finished job")


def arg_handler():

    parser = argparse.ArgumentParser(description="A program to sort media")
    parser.add_argument("-i", "--input", help="path to source directory")
    parser.add_argument("-o", "--output", help="path to output directory")
    parser.add_argument("-l", "--log", help="path to log output file")
    parser.add_argument("-n", "--include", help="filetypes to include in sort")
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
