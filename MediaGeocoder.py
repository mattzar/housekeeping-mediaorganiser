from __future__ import annotations
from GPSPhoto import gpsphoto
import googlemaps
import logging
from collections import Counter
import re
from tokens import ARC_GIS_API_KEY, GOOGLE_API_KEY

# gis = GIS("https://www.arcgis.com", api_key=arcgis_api_key)

class LocationNotFound(Exception):
    pass




def get_latlng_from_exif(image):

    location = gpsphoto.getGPSData(image)

    try:
        return (
            location["Latitude"],  # `Y` is latitude
            location["Longitude"],  # `X` is longitude
        )

    except KeyError as e:
        raise LocationNotFound from e

class GoogleMapsClient:

    def __init__(self, key=GOOGLE_API_KEY):
        self.client = googlemaps.Client(key=key)

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        del self

    @staticmethod
    def locate_from_exif(image, method, **kwargs):
        try:
            latlng = get_latlng_from_exif(image)
            logging.info("GPS location found in image metadata")
            return method(latlng, **kwargs)
        except LocationNotFound:
            logging.info("GPS location not found")

    def aggregate_reverse_geocode(self, images, keys=None):

        # keys = keys or 'formatted_address',


        # def key_queue(keys):
        #     while keys:
        #         try :
        #             loc[0][keys.pop()]
        #         except KeyError:
        #             logging.info(F'location:{key}')

        # for loc in locations:

        locations = [self.reverse_geocode_from_exif(image) for image in images]

        loc_addresses = [
            0 if (isinstance(loc, int)) else loc[0]["formatted_address"]
            for loc in locations
        ]

        strip_special = re.compile(r'[^-a-zA-Z0-9.]+')
        
        loc_addresses = [" ".join(el.split(', ')[:3]) for el in loc_addresses]
        formatted_locs = [re.search('/[^a-zA-Z0-9\s]/gi','', el) for el in loc_addresses]

        c = Counter(loc_addresses)
        c.most_common(1)

    def reverse_geocode_from_exif(self, image):
        return GoogleMapsClient.locate_from_exif(image, self.client.reverse_geocode)

    def places_nearby_from_exif(self, image):
        return GoogleMapsClient.locate_from_exif(image, self.client.places_nearby)


def main():
    with GoogleMapsClient() as client:
        var = client.places_nearby_from_exif("test.jpg")

if __name__ == "__main__":
    main()