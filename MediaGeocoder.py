arcgis_api_key = 'AAPK26c56181e45c4acb80283df4d720e9c0EzYCRVfeX66Xy94U_lprALQ6rEz-oen3qdMMf5iVnlcSDbDpUw-ZljwuRlNzybuy'
# gis = GIS("https://www.arcgis.com", api_key=arcgis_api_key)


from GPSPhoto import gpsphoto
from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point

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