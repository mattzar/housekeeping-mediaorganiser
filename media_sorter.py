import os
import pathlib
import shutil
from shutil import Error
import re
import logging
from pathlib import Path

import yaml
import tools_utilities as util
import tools_metadata as meta
import media_geocoder as geo

def parse_job(params):

    with open('settings.yaml', 'r') as file:
        settings = yaml.safe_load(file)

    job = dict(
        input=Path(params.input or Path.home() / settings["defaults"]["input"]),
        output=Path(params.output or Path.home() / settings["defaults"]["output"]),
        log=Path(params.log or Path.home() / settings["defaults"]["log"]),
        verbose=params.verbose or settings["defaults"]["verbose"],
        extensions=params.include or tuple(settings["defaults"]["extensions"]),
        foldernames=params.foldernames or settings["defaults"]["foldernames"],
    )

    try:
        job["exclusions"] = params.exclude.split(" ")
    except AttributeError:
        job["exclusions"] = settings["defaults"]["exclusions"]
    return job


def process_job(job):

    os.makedirs(os.path.dirname(job["log"].parent), exist_ok=True)

    logging.basicConfig(
        filename=job["log"],
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    logging.info("Starting job")

    queue = util.list_filepaths_in_dir(job["input"], job["extensions"])

    # remove any exluded files
    regex = [re.compile(ex) for ex in job["exclusions"]]
    queue = [i for i in queue if not (any(ex.search(i) for ex in regex))]

    if job["foldernames"] == "location":
        locations = geo.aggregate_reverse_geocode(queue)

    while queue:
        image = queue.pop()

        if job["foldernames"] == "date":
            folder, message = meta.get_date_from_image_filename(image, "%Y-%M")
        elif job["foldernames"] == "location":
            folder, message = locations[0]

        util.log_output(job, image, message)

        try:
            pathlib.Path(job["output"] / folder).mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(image, job["output"] / folder)

            except Error:
                util.log_output(job, image, "Cannot move file, copying instead")
                shutil.copy(image, job["output"] / folder)

        except PermissionError:
            queue.insert(0, image)
            util.log_output(
                job,
                image,
                "is currently not available, sending to back of queue and continuing",
            )

    logging.info("Finished job")


def main():
    pass


if __name__ == "__main__":
    main()
