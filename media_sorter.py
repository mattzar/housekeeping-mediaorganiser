import os
import pathlib
import shutil
from shutil import Error
import re
import logging
from pathlib import Path
import sys
from log_formatter import setup_logging
import argparse

import yaml
import tools_utilities as util
import tools_metadata as meta
import media_geocoder as geo

class Job:

    def __init__(self, params=None):

        with open('settings.yaml', 'r') as file:
            settings = yaml.safe_load(file)

        self.input=Path(params.input or Path.home() / settings["defaults"]["input"])
        self.output=Path(params.output or Path.home() / settings["defaults"]["output"])
        self.log=Path(params.log or Path.home() / settings["defaults"]["log"])
        self.verbose=params.verbose or settings["defaults"]["verbose"]
        self.extensions=params.include or tuple(settings["defaults"]["extensions"])
        self.foldernames=params.foldernames or settings["defaults"]["foldernames"]

        try:
            self.exclusions = params.exclude.split(" ")
        except AttributeError:
            self.exclusions = settings["defaults"]["exclusions"]

def arg_handler():

    parser = argparse.ArgumentParser(description="A program to sort media")
    parser.add_argument(
        "-v", "--verbose", help="enable verbose mode", action="store_true"
    )
    parser.add_argument("-i", "--input", help="path to source directory")
    parser.add_argument("-o", "--output", help="path to output directory")
    parser.add_argument("-l", "--log", help="path to log output file")
    parser.add_argument("-n", "--include", help="filetypes to include in sort")
    parser.add_argument("-x", "--exclude", help="wildcarded names to exclude")
    parser.add_argument("-f", "--foldernames", help="wildcarded names to exclude")

    return parser.parse_args()

def process_job(job):

    # os.makedirs(os.path.dirname(job["log"].parent), exist_ok=True)

        # Setup logging
    if (not setup_logging(console_log_output="stdout", console_log_level="debug", console_log_color=True,
                        logfile_file=job.log, logfile_log_level="debug", logfile_log_color=False,
                        log_line_template="%(color_on)s[%(created)d] [%(threadName)s] [%(levelname)-8s] %(message)s%(color_off)s")):
        print("Failed to setup logging, aborting.")
        return 1

    # logging.basicConfig(
    #     filename=job["log"],
    #     encoding="utf-8",
    #     level=logging.DEBUG,
    #     format="%(asctime)s %(message)s",
    #     datefmt="%m/%d/%Y %I:%M:%S %p",
    # )

    logging.info("Starting job")

    input = util.list_filepaths_in_dir(job.input, job.extensions)
    existing = [os.path.basename(elem) for elem in util.list_filepaths_in_dir(job.output, job.extensions)]
    queue = [elem for elem in input if os.path.basename(elem) not in existing]

    # remove any exluded files
    regex = [re.compile(ex) for ex in job.exclusions]
    queue = [i for i in queue if not (any(ex.search(i) for ex in regex))]

    logging.info(f"{len(input)} files found in input folder")
    logging.info(f"{len(existing)} files found in output folder")
    logging.info(f"{len(queue)} files added to job queue")

    if job.foldernames == "location":
        locations = geo.aggregate_reverse_geocode(queue)

    while queue:
        image = queue.pop()

        if job.foldernames == "date":
            folder, message = meta.get_date_from_image_filename(image, "%Y-%M")
        elif job.foldernames == "location":
            folder, message = locations[0]

        logging.info(message)

        try:
            pathlib.Path(job.output / folder).mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(image, job.output / folder)

            except Error:
                logging.info(f"{image}: Cannot move file, copying instead")
                shutil.copy(image, job.output / folder)

        except PermissionError:
            queue.insert(0, image)
            logging.info("f{image} is currently not available, sending to back of queue and continuing")

    logging.info("Finished job")


def main():

    args = arg_handler()
    job = Job(args)
    process_job(job)


if __name__ == "__main__":
    sys.exit(main())
