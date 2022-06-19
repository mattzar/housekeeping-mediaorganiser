from __future__ import annotations
import os
import pathlib
import shutil
import re
import logging
import sys
from LogFormatter import setup_logging
import argparse
import yaml

import tools_utilities as util
import tools_metadata as meta
import media_geocoder as geo
from FileSorter import ImageByDateSorter, ImageByLocationSorter
from FileSearch import DirectorySearch, RemovableDriveSearch


class MediaSorter:
    def __init__(self, params=None):

        settings_path = pathlib.Path(os.getcwd(), "settings.yaml")
        with open(settings_path, "r") as file:
            settings = yaml.safe_load(file)

        defaults = settings["defaults"] | settings["jobs"][params.job] if params.job else settings["defaults"]
        self.input = pathlib.Path(params.input or defaults["input"])
        self.output = pathlib.Path(params.output or defaults["output"])
        self.log = pathlib.Path(
            params.log or settings["defaults"]["output"] + defaults["log"]
        )
        self.loglevel = params.loglevel or defaults["loglevel"]
        self.extensions = params.include or tuple(defaults["extensions"])
        self.foldernames = params.foldernames or defaults["foldernames"]
        self.method = params.method or defaults["method"]

        try:
            self.exclusions = params.exclude.split(" ")
        except AttributeError:
            self.exclusions = defaults["exclusions"]

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
            exit()

    def process_job(self):

        logging.info("Starting job")


        # if input is set to removable drives, look for files of type self.extensions
        # otherwise look for files in the defined input directory
        if self.input.name == "removables":
            input_files = RemovableDriveSearch().find_files(
                extensions=self.extensions,
            ).exclude_files(self.exclusions)
        else:
            input_files = DirectorySearch().find_files(
                extensions=self.extensions, 
                directory=self.input
            ).exclude_files(self.exclusions)
        
        existing_files = DirectorySearch().find_files(
            extensions=self.extensions, 
            directory=self.output
        )
        # Form queue of files of type in 'extensions', which are in input but not already in output (avoids duplicates)
        queue = [file for file in input_files.filenames if file not in existing_files.filenames]

        logging.info(f"{len(input_files)} files found in input folder: {self.input}")
        logging.info(f"{len(existing_files)} files found in output folder: {self.output}")
        logging.info(f"{len(queue)} files added to job queue")

        if self.foldernames == "location":
            with geo.GoogleMapsClient() as client:
                locations = client.aggregate_reverse_geocode(queue)

        while queue:

            image = queue.pop()

            if self.foldernames == "date":
                sorter = ImageByDateSorter()

            elif self.foldernames == "location":
                # Experimental
                sorter = ImageByLocationSorter()
            
            sorter.sort(
                filepath=image,
                destination=self.output,
                method=self.method
            )

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
