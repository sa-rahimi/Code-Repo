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

if __name__ == '__main__':        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    search_criteria = 'Composit_CZ_Area5h_Dep20m.shp'
    f_dir = os.path.join(dir_path, search_criteria)
    capture_zones = gpd.read_file(f_dir)
    capture_zones.plot(column='OrderStrah', figsize=(12, 8)) ## 'OrderStrah' can be changed to any attribute in the shapefile
    capture_zones

    print(f'This is to compare the speed of CPU and GPU over a normal vector analysis,',
          f'"intersecting two vectors",',
          f'one with "{base_lyr.size}" and another with "{overlay_lyr.size}" polygons.',
          f'\n\nThis analysis takes: ')

    """
    Find the last segments of a channel link, where it joins a bigger channel (drain_nodes).
        Channels with order 1 are excluded as they only contain one segment.
    """
    drain_nodes = capture_zones.where((capture_zones['OrderStrah'] <
                                       capture_zones['TargetOrd']) & (capture_zones['OrderStrah'] > 1))

    drain_nodes = capture_zones[(capture_zones['OrderStrah'] < capture_zones['TargetOrd']) & (capture_zones['OrderStrah'] > 1)]
    drain_nodes = drain_nodes[drain_nodes['OrderStrah'] != 7] ## Take the last stream out, because it covers the entire catchment and takes time.
    drain_nodes = drain_nodes[['Stream', 'OrderStrah']]
    drain_nodes = drain_nodes.sort_values(by=['OrderStrah'], ascending=True)
    drain_nodes

##    start = timer()
##    res_intersect = poly_intersect_gpu(base_lyr, overlay_lyr)
##    cuda.profile_stop()
##    print('    ', timer()-start, 'seconds, on single CPU with GPU')
##
##    start = timer()
##    res_intersect = parallelize_gpu()
##    cuda.profile_stop()
##    print('    ', timer()-start, 'seconds, on 40 CPUs with GPU')
##
##    
