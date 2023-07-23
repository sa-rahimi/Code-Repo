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


def mosaic(path):
    # Search and read raster files
    search_criteria = '*.tif'
    q = os.path.join(path, search_criteria)
    raster_files = glob.glob(q)

    # mosaic rasters and stor them in a gdal virtual file in the memory
    mosaic_raster = gdal.BuildVRT('', raster_files)
    print('All files have been read')
    
    return mosaic_raster



def reproject(vrt_mosaic):
    # reproject the raster and stor it in a gdal virtual file in the memory
    reprj_raster = gdal.Warp('', vrt_mosaic, format='vrt', dstSRS='EPSG:2193')

    return reprj_raster



def compress(vrt_mosaic):
    # compress the raster and write it into a TIFF file
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co ZLEVEL=9 -co BIGTIFF=YES'))
    compressed = os.path.join(dir_path, 'Mosaic_Reprojected_Compressed.tif')
    gdal.Translate(compressed, vrt_mosaic, options=translateoptions)



if __name__ == '__main__':
    vrt_mosaic = mosaic(dir_path)
    vrt_reproject = reproject(vrt_mosaic)
    compress(vrt_reproject)
