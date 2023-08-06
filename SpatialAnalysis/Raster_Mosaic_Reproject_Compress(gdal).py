import os
import glob
import rasterio as rio
from rasterio.merge import merge
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal


# Mosaic all rasters in a directory
def mosaic(path):
    # Search and read raster files
    search_criteria = '*.tif'
    q = os.path.join(path, search_criteria)
    raster_files = glob.glob(q)
    # mosaic rasters and stor them in a gdal virtual file in the memory
    mosaic_raster = gdal.BuildVRT('', raster_files)
    print('All files have been read')
    return mosaic_raster

# Reproject the raster
def reproject(path, dst_SRS):
    # Open the raster files
    r_file = gdal.Open(path)
    # Reproject the raster and stor it in a gdal virtual file in the memory
    reprj_raster = gdal.Warp('', r_file, format='vrt', dstSRS=dst_SRS)
    return reprj_raster

# Resample the raster
def resample(path, x_res, y_res):
    # Open the raster files
    r_file = gdal.Open(path)
    # Resample the raster using the GRA_Bilinear resampling algorithm
    resamp_raster = gdal.Warp('', r_file, format = 'vrt',
                                 xRes = x_res, yRes = y_res, resampleAlg = gdal.GRA_Bilinear)
    return resamp_raster

# Combine a big lower resolution rster with smaller higher reolution raster(s)
def update_georaster(source_path, target_path):
    # Open the source and target raster files
    source_dataset = gdal.Open(source_path, gdal.GA_Update) # The raster that needs to be updated
    target_dataset = gdal.Open(target_path, gdal.GA_ReadOnly) # The raster that is used to update the other raster
    gdal.Warp(source_dataset, target_dataset, options=gdal.WarpOptions(dstNodata=-9999))
    source_dataset = None
    target_dataset = None

# Compress and save the raster
def compress_save(r_file, out_name):
    # Compress the raster and write it into a TIFF file
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co ZLEVEL=9 -co BIGTIFF=YES'))
#     translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine('-of GTiff -co BIGTIFF=YES'))
    gdal.Translate(out_name, r_file, options=translateoptions)


if __name__ == '__main__':    
    # Change the current working directory
    os.chdir(r'D:\LWS Projects\South Canterbury Catchment Collective\2 Working Files\Working Datasets\1 - Spatial Data\Combined_CompositeLiDAR_DEM1m')
    # Mosaic all the rasters in the specified directory
#     vrt_mosaic = mosaic(path=os.getcwd())
    
    # Reproject the raster
#     vrt_reproject = reproject(path='', 'EPSG:2193')

    # Resample the raster file
#     vrt_resample = resample('./Combined_LiDAR_Composite_DEM1m.tif', 2, 2)
    
    # Aligned the target raster with the source raster
#     vrt_aligned = align_georasters(source_path = './WAI_Wanaka_CompositeDEM1m.tif',
#                                    target_path = './WAI_Wanaka_LiDAR_DEM1m.tif')
    
#     update_georaster('./Combined_LiDAR_Composite_DEM1m.tif', './New_LiDAR.tif')
    r_file = gdal.Open('./Combined_LiDAR_Composite_DEM1m.tif')
    # Compress and Save the raster in the working directory
    compress_save(r_file, out_name='./Combined_Composite_LiDAR_DEM11m.tif')

