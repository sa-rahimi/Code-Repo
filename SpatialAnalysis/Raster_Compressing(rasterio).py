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
search_criteria = "*.tif"
q = os.path.join(dir_path, search_criteria)
raster_files = glob.glob(q)

for file in raster_files:
    with rio.open(file) as src:
        raster = src.read(1, masked=True)
        meta = src.meta.copy()
        
    fname = os.path.basename(file)
    compressed = os.path.join(dir_path, 'Compressed_' + fname)


    with rio.open(compressed, 'w', **meta, COMPRESS='LZW') as dest:
            dest.write(raster, 1)
    print('Raster file ' + fname + ' has been created')


