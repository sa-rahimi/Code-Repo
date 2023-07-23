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




if __name__ == '__main__':
    start_time = time.ctime()
    print("\nThe program started at: ", start_time)
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    search_criteria = 'vegetation.shp'
    base_dir = os.path.join(dir_path, search_criteria)
    base_layer = gpd.read_file(base_dir)
    print ('\nBase shapefile has been successfuly loaded')

    n_parts = 10
    chunks = np.array_split(base_layer, n_parts)
    parcel_chunks = [gpd.GeoDataFrame.from_features(chunk) for chunk in chunks]

    i = 1
    for row in parcel_chunks:
        out_dir = os.path.join(dir_path, f'chunk_{i}.shp')
        row.to_file(out_dir)
        i = i + 1
    
    print('\nBe patient crazy, you have given me a huge task')
    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')

