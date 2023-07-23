import os
import glob
import geopandas as gpd
import time

start_time = time.ctime()
print("\nThe program started at: ", start_time)
    
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

search_criteria = 'LUCAS_intersected_Livestock.shp'
base_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(base_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'LUCAS_intersected_Livestock_p.shp'
join_dir = os.path.join(dir_path, search_criteria)
join_layer = gpd.read_file(join_dir)
print ('\njoin shapefile has been successfuly loaded')

def spatial_join(base_layer, join_layer):
    res_intersect = gpd.sjoin(base_layer, join_layer, how='inner')
##    base_layer.sjoin(join_layer, how="inner", predicate='intersects')
    return res_intersect

if __name__ == '__main__':
    res_intersect = spatial_join(base_layer, join_layer)
    out_dir = os.path.join(dir_path, 'res_intersect.shp')
    res_intersect.to_file(out_dir)

    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')
