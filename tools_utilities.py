from datetime import datetime
import os
import re
import platform
from datetime import datetime, timedelta

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def round_to_secs(dt: datetime) -> datetime:
    extra_sec = round(dt.microsecond / 10**6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)


def get_date_from_string(string):
    # first look for 8 digits in string
    if dateString := re.compile(r"\b\d{8}\b").search(string):
        # Check if found date is valid, and if so return date_time object
        date_time = datetime.strptime(dateString.group(0), "%Y%m%d")
        if datetime(1900, 1, 1) <= date_time <= datetime.today():
            return date_time
    # otherwise return 0
    return 0


def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        # return os.path.getctime(path_to_file)
        return os.stat(path_to_file).st_mtime
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def list_filepaths_in_dir(directory, ext):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                path = os.path.join(root, file)
                filepaths.append(path)
    return filepaths