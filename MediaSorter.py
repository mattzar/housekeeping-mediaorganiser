from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
import os
import pathlib
import shutil
from shutil import Error
import platform
from datetime import datetime, timezone, timedelta
from termcolor import colored
import re
import logging
from pathlib import Path

from settings import defaults

# Utility Functions
# ********************************************************

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def round_to_secs(dt: datetime) -> datetime:
    extra_sec = round(dt.microsecond / 10 ** 6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)

def get_date_from_string(string):
    # first look for 8 digits in string
    if (dateString := re.compile(r'\b\d{8}\b').search(string)):
        # Check if found date is valid, and if so return date_time object
        date_time = datetime.strptime(dateString.group(0), '%Y%m%d')
        if datetime(1900,1,1) <= date_time <= datetime.today():
            return date_time
    # otherwise return 0
    return 0

def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        #return os.path.getctime(path_to_file)
        return os.stat(path_to_file).st_mtime
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def get_list_filepaths_in_dir(directory, ext):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                path = os.path.join(root, file)
                filepaths.append(path)
    print(f'{len(filepaths)} files added to queue')
    return filepaths

# Class Definitions
# ********************************************************

class MediaSorter():

    def __init__(self):
        pass
    
    def prepare_job(self, params):

        job = {}
        job["input"] = Path(params.input or Path.home()/defaults["input"])
        job["output"] = Path(params.output or Path.home()/defaults["output"])
        job["log"] = Path(params.log or Path.home()/defaults["log"])
        job["verbose"] = params.verbose or defaults["verbose"]
        job["extensions"] = params.include or defaults["extensions"]

        try:
            job["exclusions"] = params.exclude.split(" ")
        except AttributeError: 
            job["exclusions"] = defaults["exclusions"]
        return job

    def get_metadata_from_exif(self, filename):

        try:
            image = Image.open(filename)
            image.verify()
        except UnidentifiedImageError:
            logging.error('Unidentified image error')
            return 0
        except Exception:
            logging.error('File is broken')
            return 0

        exifdata = image.getexif()
        metadata = {}

        # iterating over all EXIF data fields
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes if required
            if isinstance(data, bytes):
                try:
                    data = data.decode()
                except UnicodeDecodeError:
                    logging.error(f'unable to decode {tag}')
            metadata[tag] = data
        
        return metadata

    def process_job(self, job):

        logging.basicConfig(
            filename=job['log'],
            mode='a',
            encoding='utf-8',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )

        queue = get_list_filepaths_in_dir(job['input'], job['extensions'])

        # remove any exluded files
        regex = [re.compile(ex) for ex in job['exclusions']]
        queue = [i for i in queue if not(any(ex.search(i) for ex in regex))]

        while len(queue)>0:
            image = queue.pop()
            folder = ""
            success = False
            # first look for 8 digits in filename
            if (filename_date := get_date_from_string(image)):
                folder = filename_date.strftime("%Y-%m")
                self.log_output(job, image, 'valid date extracted from filename')
                success = True

            # Then check for metadata present
            elif (metadata := self.get_metadata_from_exif(image)):
                try:
                    # if metadata present, look for 'DateTime' info
                    folder = '-'.join(metadata["DateTime"].split(' ')[0].split(':')[:2])
                    self.log_output(job, image, 'using DateTime from metadata')
                    success = True
                except KeyError:
                    # If DateTime not present, then notify user and pass
                    self.log_output(job, image, 'DateTime not present in metadata')
                    pass
            if not(success):
                # otherwise determine creation date and use that instead
                folder = datetime.fromtimestamp(get_creation_date(image), tz=timezone.utc).strftime('%Y-%m')
                self.log_output(job, image, 'Using creation date to file')   
                
            try:
                pathlib.Path(job['output']/folder).mkdir(parents=True, exist_ok=True)
                try:
                    dest = shutil.move(image, job['output']/folder)
                except Error:
                    self.log_output(job, image, 'Cannot move file, copying instead')
                    dest = shutil.copy(image, job['output']/folder)
            except PermissionError:    
                queue.insert(0, image)
                self.log_output(job, image, 'is currently not available, sending to back of queue and continuing')

    def log_output(self, job, obj, message):
        now = round_to_secs(datetime.now())
        with open(job['output']/job['log'], "a") as f:
            f.write(f'{now} {obj} : {message}\n')
        obj = colored(obj, 'white')
        message = colored(message, 'green')
        if job['verbose']:
            print(f'{now} {obj} : {message}')

def main():

    pass

if __name__ == '__main__':
    main()