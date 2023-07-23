import os
import glob
import rtree
import numpy as np
import geopandas as gpd
import pandas as pd
import multiprocessing as mp
from shapely.geometry import Polygon

import numba
from numba import jit
from numba import cuda
from timeit import default_timer as timer

# To run on GPU
@jit   
def poly_intersect_gpu(base, overlay):
    res_intersect = gpd.overlay(base, overlay, how='intersection')
    return res_intersect

# To run on CPU
def poly_intersect_cpu(base, overlay):
    res_intersect = gpd.overlay(base, overlay, how='intersection')
    return res_intersect


chunk_results = []
def collect_result(result):
    global chunk_results
    chunk_results.append(result)
    
def parallelize_cpu():
    nCPU = 40 #round(mp.cpu_count() * 0.8)
    
    chunks = np.array_split(base_lyr, nCPU)
    parcel_chunks = [gpd.GeoDataFrame.from_features(chunk) for chunk in chunks]
    
    pool = mp.Pool(processes=nCPU)
    chunk_processes = [pool.apply_async(poly_intersect_cpu, args=(chunk, overlay_lyr), callback=collect_result)
                       for chunk in parcel_chunks]
    pool.close()
    pool.join()
    
    res_intersect = gpd.GeoDataFrame(pd.concat(chunk_results))
    return res_intersect

def parallelize_gpu():
    nCPU = 40 #round(mp.cpu_count() * 0.8)
    
    chunks = np.array_split(base_lyr, nCPU)
    parcel_chunks = [gpd.GeoDataFrame.from_features(chunk) for chunk in chunks]
    
    pool = mp.Pool(processes=nCPU)
    chunk_processes = [pool.apply_async(poly_intersect_gpu, args=(chunk, overlay_layer), callback=collect_result)
                       for chunk in parcel_chunks]
    pool.close()
    pool.join()
    
    res_intersect = gpd.GeoDataFrame(pd.concat(chunk_results))
    return res_intersect


if __name__ == '__main__':        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    search_criteria = 'vec_lyr_1.shp'
    base_dir = os.path.join(dir_path, search_criteria)
    base_lyr = gpd.read_file(base_dir)

    search_criteria = 'vec_lyr_2.shp'
    overlay_dir = os.path.join(dir_path, search_criteria)
    overlay_lyr = gpd.read_file(overlay_dir)

    print(f'This is to compare the speed of CPU and GPU over a normal vector analysis,',
          f'"intersecting two vectors",',
          f'one with "{base_lyr.size}" and another with "{overlay_lyr.size}" polygons.',
          f'\n\nThis analysis takes: ')

    start = timer()
    res_intersect = poly_intersect_cpu(base_lyr, overlay_lyr)
    print('    ', timer()-start, 'seconds, on single CPU without GPU')

    start = timer()
    res_intersect = poly_intersect_gpu(base_lyr, overlay_lyr)
    cuda.profile_stop()
    print('    ', timer()-start, 'seconds, on single CPU with GPU')

    start = timer()
    res_intersect = parallelize_cpu()
    print('    ', timer()-start, 'seconds, on 40 CPUs without GPU')

    start = timer()
    res_intersect = parallelize_gpu()
    cuda.profile_stop()
    print('    ', timer()-start, 'seconds, on 40 CPUs with GPU')
    
##    start = timer()
##    res_intersect = poly_intersect_gpu(base_layer, overlay_layer)
##    cuda.profile_stop()
##    print("with GPU:", timer()-start)


##    out_dir = os.path.join(dir_path, 'res_chunks.shp')
##    res_intersect.to_file(out_dir)

