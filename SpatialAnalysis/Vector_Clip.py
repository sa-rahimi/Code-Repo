import os
import glob
import rtree
import numpy as np
from osgeo import gdal
import geopandas as gpd
import pandas as pd
import multiprocessing as mp
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import time


start_time = time.ctime()
print("\nThe program started at: ", start_time)
    
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

search_criteria = 'NRC_Primary_Parcel.shp'
input_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(input_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'Wairoa_Landuse_06092021_1320.shp'
clip_dir = os.path.join(dir_path, search_criteria)
clip_layer = gpd.read_file(clip_dir)
print ('\nclip shapefile has been successfuly loaded')

res_clip = gpd.clip(base_layer, clip_layer)
out_dir = os.path.join(dir_path, 'res_clip.shp')
res_clip.to_file(out_dir)

end_time = time.ctime()
print('\nThe program started at: ', end_time)
print('\nDuane: I love you and I am in your service Land and Water Science')
