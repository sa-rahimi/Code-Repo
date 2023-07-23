import os
import glob
import rtree
import numpy as np
from osgeo import gdal, ogr
from osgeo.gdalconst import *
import geopandas as gpd
import pandas as pd
import multiprocessing as mp
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import time
import sys

## Test
if __name__ == "__main__": 
    start_time = time.ctime()
    print("\nThe program started at: ", start_time)

    gdal.PushErrorHandler('CPLQuietErrorHandler')
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    
    # Read the transfer raster layer
    search_criteria = 'Kaipara_SPAL_deposition_susceptibility_class.tif'
    trans_dir = os.path.join(dir_path, search_criteria)
    trans_lyr = gdal.BuildVRT('', trans_dir)
##    trans_lyr = gdal.Open(trans_dir, 1)

    # Get the projection of the raster
    trans_project = trans_lyr.GetProjection()

    # Get the GeoTransform of the raster
    trans_geo = trans_lyr.GetGeoTransform()

    # change the position of the raster's origion. In this case 10 m towards right (one pixel size)
    trans_geo_new = (trans_geo[0] + trans_geo[1], trans_geo[1], trans_geo[2], trans_geo[3], trans_geo[4], trans_geo[5])

    # Set new values to origin of the layer
    trans_lyr.SetGeoTransform(trans_geo_new)

    # after shifting I found the projection gets reset and needs to be specified again, so I import it from reference image)
    trans_lyr.SetProjection(trans_project)

    # Write the raster
    fname = os.path.basename(trans_dir)
    moved = os.path.join(dir_path, 'Moved_L1D1_' + fname)
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co PREDICTOR=2 -co ZLEVEL=9 -co BIGTIFF=YES'))
    gdal.Translate(moved, trans_lyr, options=translateoptions)
   
    end_time = time.ctime()
    print("\nThe program finished at: ", end_time)
