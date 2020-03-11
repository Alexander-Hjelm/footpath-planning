from geojson import FeatureCollection, dump
import fiona

shapes = fiona.open("raw_data/ay_get.shp")
print(shapes.schema)
#first feature of the shapefile
#first = shapes.next()
data_out = []

for i in range(0, len(shapes)):
    data_out.append(shapes[i])
    #print(shapes[i]) # (GeoJSON format)

with open('raw_data/plots.geojson', 'w') as f:
    dump(FeatureCollection(data_out), f)
