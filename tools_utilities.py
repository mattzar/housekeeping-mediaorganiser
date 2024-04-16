import os
import re
import platform
from datetime import datetime, timedelta
from typing import Any, List
import psutil
import logging
import pathlib
import time
import hashlib

class ValidDateNotFound(Exception):
    """A valid date cannot be extracted from the filename"""

def st_time(func):
    """
        st decorator to calculate the total time of a func
    """

    def st_func(*args, **keyArgs):
        t1 = time.time()
        r = func(*args, **keyArgs)
        t2 = time.time()
        print(f"Function={func.__name__}, Time={t2 - t1}")
        return r

    return st_func
    
def iterable(obj: Any) -> bool:
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def find_files_on_removable_drives(extensions: List[str]) -> List[pathlib.Path]:

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

def get_date_from_string(string : str, format:dict):
    # first look for 8 digits in string
    # if dateString := re.compile(r"\d{8}").search(string):
    # Updated based on https://stackoverflow.com/questions/51224/regular-expression-to-match-valid-dates
    # if dateString := re.compile(r"\b(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|30|31)\b").search(string):
    if dateString := re.compile(format['regex']).search(string):
        # Check if found date is valid, and if so return date_time object
        try:
            date_time = datetime.strptime(dateString[0], format['dateformat'])
        except ValueError as e:
            raise ValidDateNotFound from e
        if datetime(1900, 1, 1) <= date_time <= datetime.now():
            return date_time
    # otherwise return 0
    raise ValidDateNotFound

def get_creation_date(path_to_file: str | pathlib.Path) -> Any:
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

def list_filepaths_in_dir(directory : str | pathlib.Path, ext : List[str]) -> List[pathlib.Path]:
    return [filepath for filepath in pathlib.Path(directory).rglob("**/*") if filepath.suffix.casefold() in map(str.casefold, ext)]

def rename_files_with_suffix(folder_path, suffix='2'):
    # List all files in the folder
    files = os.listdir(folder_path)

    for filename in files:
        # Construct the old and new file paths
        old_path = os.path.join(folder_path, filename)
        new_filename = f"{os.path.splitext(filename)[0]}_{suffix}{os.path.splitext(filename)[1]}"
        new_path = os.path.join(folder_path, new_filename)

        # Check if the new filename already exists
        if not os.path.exists(new_path):
            # Rename the file
            os.rename(old_path, new_path)
            print(f'Renamed: {filename} to {new_filename}')
        else:
            print(f'Skipped renaming {filename} as {new_filename} already exists.')


def compute_checksum(file_path: str, algorithm='md5') -> str:
    """Compute checksum of a file."""
    hash_algorithm = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_algorithm.update(chunk)
    return hash_algorithm.hexdigest()

def main():
    # Provide the path to the folder containing the files
    folder_path = 'path/to/folder'

    # Call the function to rename files in the folder
    rename_files_with_suffix(folder_path)

if __name__ == "__main__":
    main()