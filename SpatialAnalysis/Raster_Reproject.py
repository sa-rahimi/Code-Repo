import os
import glob
import rasterio
from osgeo import gdal

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

search_criteria = '*.tif'
q = os.path.join(dir_path, search_criteria)
dir_files = glob.glob(q)
print(str(len(dir_files)) + ' rasters are ready to be reprojected')

def reproject(directory):
    print(directory)
    input_raster = gdal.Open(directory)
    file = os.path.basename(directory)
    file_name = os.path.splitext(file)[0]
    output_raster = os.path.join(dir_path, file_name + '_re.tif')
    
    translateoptions = gdal.TranslateOptions(
        gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co ZLEVEL=9 -co BIGTIFF=YES'))

    warp = gdal.Warp(output_raster,input_raster,dstSRS='EPSG:2193')
    warp = None # Closes the files

for dir in dir_files:
    reproject(dir)
