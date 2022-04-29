
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from datetime import timezone
import logging

from tools_utilities import *

def get_metadata_from_exif(filename):

    try:
        image = Image.open(filename)
        image.verify()
    except UnidentifiedImageError:
        logging.error("Unidentified image error")
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

def get_date_from_image_filename(filename, format):

    # first look for 8 digits in filename
    if filename_date := get_date_from_string(filename):
        folder = filename_date.strftime(format)
        return folder, "valid date extracted from filename"

    elif metadata := get_metadata_from_exif(filename):
        # Then check for metadata present
        try:
            # if metadata present, look for 'DateTime' info
            folder = "-".join(metadata["DateTime"].split(" ")[0].split(":")[:2])
            return folder, "using DateTime from metadata"
        except KeyError:
            logging.info("No datetime present in metadata")
    else:
        # otherwise determine creation date and use that instead
        logging.info("Using file creation date as nothing better was detected")
        folder = datetime.fromtimestamp(get_creation_date(filename)).astimezone().strftime(format)
        return folder, "Using creation date to file"