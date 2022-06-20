import os
import re
import platform
from datetime import datetime, timedelta
from typing import Any, List
import psutil
import logging
import pathlib

class ValidDateNotFound(Exception):
    """A valid date cannot be extracted from the filename"""

def iterable(obj: Any) -> bool:
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def find_files_on_removable_drives(extensions: List[str]) -> List[str]:

    found_files = []
    logging.info(
        f"Searching for files of type {extensions} on removable drives"
    )

    # Find all removable partitions
    removable_drives = [
        part
        for part in psutil.disk_partitions()
        if "removable" in part.opts.split(",")
    ]
    logging.info(f"{len(removable_drives)} removable drives found")

    for drive in removable_drives:
        found_files += list_filepaths_in_dir(
            drive.mountpoint, extensions
        )
    return found_files

def round_to_secs(dt: datetime) -> datetime:
    extra_sec = round(dt.microsecond / 10**6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)

def get_date_from_string(string : str):
    # first look for 8 digits in string
    if dateString := re.compile(r"\d{8}").search(string):
        # Check if found date is valid, and if so return date_time object
        date_time = datetime.strptime(dateString[0], "%Y%m%d")
        if datetime(1900, 1, 1) <= date_time <= datetime.now():
            return date_time
    # otherwise return 0
    raise ValidDateNotFound

def get_creation_date(path_to_file: str | pathlib.Path) -> str:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        # return os.path.getctime(path_to_file)
        return os.stat(path_to_file).st_mtime
    stat = os.stat(path_to_file)
    try:
        return stat.st_birthtime
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return stat.st_mtime

def walk(path): 
    for p in pathlib.Path(path).iterdir(): 
        if p.is_dir(): 
            yield from walk(p)
            continue
        yield p.resolve()

def list_filepaths_in_dir(directory : str | pathlib.Path, ext : List[str]) -> List[pathlib.Path]:
    return [filepath for filepath in walk(directory) if filepath.suffix.casefold() in map(str.casefold, ext)]

# def list_filepaths_in_dir(directory : str, ext : List[str]) -> List[str]:
#     filepaths = []
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.endswith(ext):
#                 path = os.path.join(root, file)
#                 filepaths.append(path)
#     return filepaths

