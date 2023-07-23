import os
import glob
import rasterio as rio
from rasterio.merge import merge
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

# Search and read raster files
search_criteria = "TRI_Lidar_1m.tif"
q = os.path.join(dir_path, search_criteria)
raster_files = glob.glob(q)

for file in raster_files:
    virtualFile = gdal.BuildVRT('', file)
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co PREDICTOR=2 -co ZLEVEL=9 -co BIGTIFF=YES'))
    fname = os.path.basename(file)
    compressed = os.path.join(dir_path, 'Compressed_' + fname)
    gdal.Translate(compressed, virtualFile, options=translateoptions)


