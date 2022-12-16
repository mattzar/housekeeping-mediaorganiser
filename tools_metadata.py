from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
import logging
from datetime import datetime
from tools_utilities import get_date_from_string, get_creation_date, ValidDateNotFound
from pathlib import Path

def get_metadata_from_exif(filepath : Path) -> dict:

    try:
        image = Image.open(filepath)
        image.verify()
    except UnidentifiedImageError:
        logging.info(f"{filepath.name} was not recognized as image")
        raise

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
                logging.error(f"unable to decode {tag}")
        metadata[tag] = data

    return metadata

def get_date_from_image_file(filepath : Path, format:dict = None) -> datetime:

    # First look for 8 digits in filename
    try:
        date = get_date_from_string(filepath.name, format)
        logging.info(f"Valid date extracted from {filepath.name}")
        return date
    except ValidDateNotFound:
        logging.info(f"Valid date not detected in {filepath.name}")
    
    # If that doesnt work, look for metadata from exif
    try:
        date = datetime(*[int(el) for el in get_metadata_from_exif(filepath)["DateTime"].split(" ")[0].split(":")])
        logging.info(f"Using DateTime from metadata in {filepath.name}")
        return date

    except (UnidentifiedImageError, KeyError):
        logging.info(f"No datetime present in {filepath.name} metadata")

    # If that doesn't work, then get the time from the file creation date as a last resort
    date = datetime.fromtimestamp(get_creation_date(filepath)).astimezone()
    logging.info(f"Using file creation date as nothing better was detected {filepath.name}")
    return date
