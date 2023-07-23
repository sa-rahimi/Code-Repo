import os
import glob
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

def mosaic(path):
    # Search and read raster files
    search_criteria = '*.tif'
    q = os.path.join(path, search_criteria)
    raster_files = glob.glob(q)

    virtual_file = gdal.BuildVRT('', raster_files)
    print('All files have been read')
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co ZLEVEL=9 -co BIGTIFF=YES'))
    compressed = os.path.join(path, 'Mosaic_Compressed.tif')
    gdal.Translate(compressed, virtual_file, options=translateoptions)

mosaic(dir_path)
