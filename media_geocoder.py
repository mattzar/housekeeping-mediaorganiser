# arcgis_api_key = "AAPK26c56181e45c4acb80283df4d720e9c0EzYCRVfeX66Xy94U_lprALQ6rEz-oen3qdMMf5iVnlcSDbDpUw-ZljwuRlNzybuy"
google_api_key = "AIzaSyBJ2fHwnAfti99LzmISl3S3rIbf7_PmRMA"
# gis = GIS("https://www.arcgis.com", api_key=arcgis_api_key)

from GPSPhoto import gpsphoto
import googlemaps
import logging
from collections import Counter
import slugify
import re

def aggregate_reverse_geocode(images, keys=None):

    # keys = keys or 'formatted_address',


    # def key_queue(keys):
    #     while keys:
    #         try :
    #             loc[0][keys.pop()]
    #         except KeyError:
    #             logging.info(F'location:{key}')

    # for loc in locations:

    locations = [reverse_geocode_from_exif(image) for image in images]

    loc_addresses = [
        0 if (isinstance(loc, int)) else loc[0]["formatted_address"]
        for loc in locations
    ]

    strip_special = re.compile(r'[^-a-zA-Z0-9.]+')
    
    loc_addresses = [" ".join(el.split(', ')[:3]) for el in loc_addresses]
    formatted_locs = [re.search('/[^a-zA-Z0-9\s]/gi','', el) for el in loc_addresses]

    c = Counter(loc_addresses)
    c.most_common(1)


def get_latlng_from_exif(image):

    location = gpsphoto.getGPSData(image)

    try:
        return (
            location["Latitude"],  # `Y` is latitude
            location["Longitude"],  # `X` is longitude
        )

    except KeyError:
        logging.info("GPS location not found")
        return -1


def reverse_geocode_from_exif(image):
    latlng = get_latlng_from_exif(image)
    gmaps = googlemaps.Client(key=google_api_key)
    return gmaps.reverse_geocode(latlng)


def places_nearby_from_exif(image):
    latlng = get_latlng_from_exif(image)
    gmaps = googlemaps.Client(key=google_api_key)
    return (
        gmaps.places_nearby(location=latlng, radius=4000)
        if isinstance(latlng, tuple)
        else -1
    )
