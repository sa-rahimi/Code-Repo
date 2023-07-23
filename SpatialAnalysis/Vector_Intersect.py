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

search_criteria = 'base_layer.shp'
base_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(base_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'overlay_layer.shp'
overlay_dir = os.path.join(dir_path, search_criteria)
overlay_layer = gpd.read_file(overlay_dir)
print ('\nOverlay shapefile has been successfuly loaded')

def poly_intersect(base_layer, overlay_layer):
    res_intersect = gpd.overlay(base_layer, overlay_layer, how='intersection')
    return res_intersect

if __name__ == '__main__':
    res_intersect = poly_intersect(base_layer, overlay_layer)
    out_dir = os.path.join(dir_path, 'res_intersect.shp')
    res_intersect.to_file(out_dir)

    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')

