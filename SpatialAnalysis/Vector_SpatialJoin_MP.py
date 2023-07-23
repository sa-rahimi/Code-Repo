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

search_criteria = 'BaseLayer.shp'
base_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(base_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'JoinLayer.shp'
join_dir = os.path.join(dir_path, search_criteria)
join_layer = gpd.read_file(join_dir)
print ('\njoin shapefile has been successfuly loaded')

def spatial_join(gdf_chunk, gdf_complete):
    res_spatial_join = gpd.sjoin(gdf_chunk, gdf_complete, how='inner')
    return res_spatial_join

chunk_results = []
def collect_result(result):
    global chunk_results
    chunk_results.append(result)
    
def parallelize():
    nCPU = round(mp.cpu_count() * 0.8)
    
    chunks = np.array_split(base_layer, nCPU)
    parcel_chunks = [gpd.GeoDataFrame.from_features(chunk) for chunk in chunks]
    print('\nBase shapefile has been devided into ' + str(nCPU) + ' chunks')
    
    pool = mp.Pool(processes=nCPU)
    chunk_processes = [pool.apply_async(spatial_join, args=(chunk, join_layer), callback=collect_result)
                       for chunk in parcel_chunks]
    print('\nBe patient crazy, you have given me a huge task')
    pool.close()
    pool.join()

    print('\nI am close :-)')
    
    res_spatial_join = gpd.GeoDataFrame(pd.concat(chunk_results), crs=base_layer.crs)

    return res_spatial_join

if __name__ == '__main__':
    res_spatial_join = parallelize()
    out_dir = os.path.join(dir_path, 'res_spatial_join.shp')
    res_spatial_join.to_file(out_dir)

    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')
