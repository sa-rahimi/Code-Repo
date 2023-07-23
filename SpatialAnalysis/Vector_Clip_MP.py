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

search_criteria = 'NRC_Primary_LUCAS_Union_QGIS.shp'
input_dir = os.path.join(dir_path, search_criteria)
base_layer = gpd.read_file(input_dir)
print ('\nBase shapefile has been successfuly loaded')

search_criteria = 'Wairoa_LCDB_08092021.shp'
clip_dir = os.path.join(dir_path, search_criteria)
clip_layer = gpd.read_file(clip_dir)
print ('\nclip shapefile has been successfuly loaded')

def poly_clip(gdf_chunk, gdf_complete):
    res_clip = gpd.clip(gdf_complete, gdf_chunk)
    return res_clip

chunk_results = []
def collect_result(result):
    global chunk_results
    chunk_results.append(result)
    
def parallelize():
    nCPU = round(mp.cpu_count() * 0.8)
    
    chunks = np.array_split(base_layer, nCPU)
    parcel_chunks = [gpd.GeoDataFrame(geometry=gpd.GeoSeries(chunk.geometry)) for chunk in chunks]
    print('\nBase shapefile has been devided into ' + str(nCPU) + ' chunks')
    
    pool = mp.Pool(processes=nCPU)
    chunk_processes = [pool.apply_async(poly_clip, args=(chunk, clip_layer), callback=collect_result)
                       for chunk in parcel_chunks]
    print('\nBe patient crazy, you have given me a huge task')
    pool.close()
    pool.join()

    print('\nI am close :-)')
    
    res_clip = gpd.GeoDataFrame(pd.concat(chunk_results), crs=base_layer.crs)

    return res_clip

if __name__ == '__main__':
    res_clip = parallelize()
    out_dir = os.path.join(dir_path, 'res_clip.shp')
    res_clip.to_file(out_dir)

    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')
