# This script reads a raw SLU export file (.shp) with buildings and processes it,
# removing any features that are not seen as buildings. It also does coordinate transformation.
# Run it first with the raw SLU data before doing anything else!
# REQUIREMENTS:
# - ./raw_data/by_get.shp
# - ./raw_data/by_get.shx

from geojson import FeatureCollection, dump
from pyproj import Proj, transform
import fiona

shapes = fiona.open("raw_data/by_get.shp")
print(shapes.schema)
#first feature of the shapefile
#first = shapes.next()
data_out = []

def polygon_area(vertices):
    n = len(vertices) # of corners
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += abs(vertices[i][0] * vertices[j][1]-vertices[j][0] * vertices[i][1])
    result = a / 2.0
    return result

def epsg3006_to_wgs84(point):
    x = point[0]
    y = point[1]
    # Coordinate conversion from EPSG:3006 to WGS:84
    # Transform using pyproj
    WGS84 = Proj('EPSG:4326')
    SWEREF = Proj('EPSG:3006',preserve_units=False)
    # Perform the transformation. SLU data has flipped x/y coordinates
    x_new, y_new = transform(SWEREF, WGS84, y, x)
    return (y_new, x_new)

for i in range(0, len(shapes)):
    shape = shapes[i]
    shape_points = []

    print("Progess: " + str(int(i*100.0/len(shapes))) + "%")

    coordinates_container = shape['geometry']['coordinates']
    for s in range(0, len(coordinates_container)):
        coordinates = coordinates_container[s]

        # Coordinate conversion
        for j in range(0, len(coordinates)):
            point = coordinates[j]
            if type(point) == tuple:
                coordinates[j] = epsg3006_to_wgs84(point)
                shape_points.append(coordinates[j])
            elif type(point) == list:
                for k in range(0, len(point)):
                    coordinates[j][k] = epsg3006_to_wgs84(coordinates[j][k])
                    shape_points.append(coordinates[j][k])
                pass
            else:
                print("ERROR: No handling for points of type: " + type(point))
    
    # Append shape to output data in GeoJSON format
    data_out.append(shape)

with open('raw_data/plots.geojson', 'w') as f:
    dump(FeatureCollection(data_out), f)
