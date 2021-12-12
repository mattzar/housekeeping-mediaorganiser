from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
from GPSPhoto import gpsphoto
from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point
import os
import pathlib
import shutil
from shutil import Error
import platform
from datetime import date, datetime, timezone, timedelta
from termcolor import colored
import time
import re

arcgis_api_key = 'AAPK26c56181e45c4acb80283df4d720e9c0EzYCRVfeX66Xy94U_lprALQ6rEz-oen3qdMMf5iVnlcSDbDpUw-ZljwuRlNzybuy'
# gis = GIS("https://www.arcgis.com", api_key=arcgis_api_key)

job = {
    'source': r'/Users/matthew/Pictures/Camera Dump/in',
    'destination': r'/Users/matthew/Pictures/Camera Dump/out/',
    'included_extensions': ('JPG', 'jpg', 'mp4', '3gp'),
    'filename_exlcusions': ('WA',),
    'log': 'log.txt',
    'verbose': False,
}

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def creation_date(path_to_file):
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

def get_files(directory, ext):
    images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                image = os.path.join(root, file)
                images.append(image)
    print(f'{len(images)} images added to queue')
    return images

def get_metadata_from_exif(filename):

    try:
        image = Image.open(filename)
        image.verify()
    except UnidentifiedImageError:
        log_output('get_metadata_from_exif', 'Unidentified image error')
        return 0
    except Exception:
        log_output('get_metadata_from_exif', 'File is broken')
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
                log_output(image, f'unable to decode {tag}')
        metadata[tag] = data
    
    return metadata

def get_date_from_string(string):
    # first look for 8 digits in string
    if (dateString := re.compile(r'\b\d{8}\b').search(string)):
        # Check if found date is valid, and if so return date_time object
        date_time = datetime.strptime(dateString.group(0), '%Y%m%d')
        if datetime(1900,1,1) <= date_time <= datetime.today():
            return date_time
    # otherwise return 0
    return 0

def round_to_secs(dt: datetime) -> datetime:
    extra_sec = round(dt.microsecond / 10 ** 6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)

def log_output(obj, message):
    now = round_to_secs(datetime.now())
    with open(job['destination'] + job['log'], "a") as f:
        f.write(f'{now} {obj} : {message}\n')
    obj = colored(obj, 'white')
    message = colored(message, 'green')
    if job['verbose']:
        print(f'{now} {obj} : {message}')

def get_named_location_from_exif(filename):

    location = gpsphoto.getGPSData(filename)
    location = {
        'Y': location['Latitude'], # `Y` is latitude
        'X': location['Longitude'], # `X` is longitude
        'spatialReference': {
            'wkid': 4326
        }
    }
    return reverse_geocode(location=Point(location))

def main():

    source = job['source']
    destination = job['destination']
    ext = job['included_extensions']
    filename_exlcusions = job['filename_exlcusions']
    imageQueue = get_files(source, ext)

    # remove any exluded files
    regex = [re.compile(ex) for ex in filename_exlcusions]
    imageQueue = [i for i in imageQueue if not(any(ex.search(i) for ex in regex))]

    while len(imageQueue)>0:
        image = imageQueue.pop()

        # first look for 8 digits in filename
        if (filename_date := get_date_from_string(image)):
            folder = filename_date.strftime("%Y-%m")
            log_output(image, 'valid date extracted from filename')

        # Then check for metadata present
        elif (metadata := get_metadata_from_exif(image)):
            try:
                # if metadata present, look for 'DateTime' info
                folder = '-'.join(metadata["DateTime"].split(' ')[0].split(':')[:2])
                log_output(image, 'using DateTime from metadata')
            except KeyError:
                # If DateTime not present, then notify user and pass
                log_output(image, 'DateTime not present in metadata')
                pass
        else:
            # otherwise determine creation date and use that instead
            folder = datetime.fromtimestamp(creation_date(image), tz=timezone.utc).strftime('%Y-%m')
            log_output(image, 'Using creation date to file')   
            
        try:
            pathlib.Path(destination+folder).mkdir(parents=True, exist_ok=True)
            try:
                dest = shutil.move(image, destination+folder)
            except Error:
                log_output(image, 'Cannot move file, copying instead')
                dest = shutil.copy(image, destination+folder)
        except PermissionError:    
            imageQueue.insert(0, image)
            log_output(image, 'is currently not available, sending to back of queue and continuing')

if __name__ == '__main__':
    main()