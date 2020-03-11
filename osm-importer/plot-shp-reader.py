from geojson import FeatureCollection, dump
import fiona

shapes = fiona.open("raw_data/ay_get.shp")
print(shapes.schema)
#first feature of the shapefile
#first = shapes.next()
data_out = []

def epsg3006_to_wgs84(point):
    x = point[0]
    y = point[1]
    # Coordinate conversion from EPSG:3006 to WGS:84
    x_new = 0.000011199*x + 10.5112561156
    y_new = 0.000009016*y
    return (x_new, y_new)


for i in range(0, len(shapes)):
    shape = shapes[i]
    coordinates = shape['geometry']['coordinates'][0]

    # Coordinate conversion
    for j in range(0, len(coordinates)):
        point = coordinates[j]
        if type(point) == tuple:
            coordinates[j] = epsg3006_to_wgs84(point)
        elif type(point) == list:
            for k in range(0, len(point)):
                coordinates[j][k] = epsg3006_to_wgs84(coordinates[j][k])
            pass
        else:
            print("ERROR: No handling for points of type: " + type(point))

    # Append shape to output data in GeoJSON format
    data_out.append(shape)

with open('raw_data/plots.geojson', 'w') as f:
    dump(FeatureCollection(data_out), f)
