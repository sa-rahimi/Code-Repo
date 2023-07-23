import os
import glob
import geopandas as gpd
import time

start_time = time.ctime()
print("\nThe program started at: ", start_time)
    
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

search_criteria = 'LU_Exotic_F.shp'
input_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(input_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'LC_Indigen_F.shp'
overlay_dir = os.path.join(dir_path, search_criteria)
overlay_layer = gpd.read_file(overlay_dir)
print ('\nOverlay shapefile has been successfuly loaded')

def poly_union(base_layer, overlay_layer):
    res_union = gpd.overlay(base_layer, overlay_layer, how='union')
    return res_union

res_union = poly_union(base_layer, overlay_layer)
out_dir = os.path.join(dir_path, 'res_union.shp')
res_union.to_file(out_dir)

end_time = time.ctime()
print('\nThe program started at: ', end_time)
print('\nDuane: I love you and I am in your service Land and Water Science')
