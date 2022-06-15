from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
import logging
from datetime import datetime
import os
from tools_utilities import get_date_from_string, get_creation_date, ValidDateNotFound

def get_metadata_from_exif(filename : str) -> dict:

    try:
        image = Image.open(filename)
        image.verify()
    except UnidentifiedImageError:
        filename = os.path.split(filename)[0]
        logging.info(f"{filename} was not recoginized as image")
        return 0
    except Exception:
        logging.error("File is broken")
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
                logging.error(f"unable to decode {tag}")
        metadata[tag] = data

    return metadata

def get_date_from_image_filename(filename : str, format : str) -> str:

    # First look for 8 digits in filename
    try:
        folder = get_date_from_string(filename).strftime(format)
        logging.info(f"Valid date extracted from {filename}")
        return folder
    except ValidDateNotFound:
        logging.info(f"Valid date not detected in {filename}")
    
    # If that doesnt work, look for metadata from exif
    try:
        folder = "-".join(get_metadata_from_exif(filename)["DateTime"].split(" ")[0].split(":")[:2])
        logging.info(f"Using DateTime from metadata in {filename}")
        return folder
    except (KeyError, TypeError):
        logging.info(f"No datetime present in metadata {filename}")

    # If that doesn't work, then get the time from the file creation date as a last resort
    folder = datetime.fromtimestamp(get_creation_date(filename)).astimezone().strftime(format)
    logging.info(f"Using file creation date as nothing better was detected {filename}")
    return folder
