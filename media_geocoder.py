# arcgis_api_key = "AAPK26c56181e45c4acb80283df4d720e9c0EzYCRVfeX66Xy94U_lprALQ6rEz-oen3qdMMf5iVnlcSDbDpUw-ZljwuRlNzybuy"
google_api_key = "AIzaSyBJ2fHwnAfti99LzmISl3S3rIbf7_PmRMA"
# gis = GIS("https://www.arcgis.com", api_key=arcgis_api_key)

from GPSPhoto import gpsphoto
import googlemaps
import logging
# from arcgis.gis import GIS
# from arcgis.geocoding import geocode, reverse_geocode
# from arcgis.geometry import Point

from collections import Counter


def aggregate_reverse_geocode(images):
    locations = [places_nearby_from_exif(image) for image in images]
    loc_addresses = [0 if (isinstance(loc, int)) else loc[0]["formatted_address"] for loc in locations]
    c = Counter(loc_addresses)
    c.most_common(1)
    print(1)

def get_latlng_from_exif(image):

    # location = gpsphoto.getGPSData(filename)
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
    return gmaps.places_nearby(location=latlng, radius=4000) if isinstance(latlng, tuple) else -1
