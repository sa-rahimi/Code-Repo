import os
import glob
import rasterio
from osgeo import gdal

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

def stacking(path):
    search_criteria = '*.tif'
    q = os.path.join(path, search_criteria)
    bandPaths = glob.glob(q)
    bandPaths.sort()
    print(str(len(bandPaths)) + ' rasters are ready to be stacked together')

    translateoptions = gdal.TranslateOptions(
        gdal.ParseCommandLine('-of GTiff -co COMPRESS=LZW -co ZLEVEL=9 -co BIGTIFF=YES'))

    virtualFile = gdal.BuildVRT('', bandPaths, separate=True)
    print('Compressing and Saving stacked image')
    stackedImage = gdal.Translate(path+'/Stacked_Image.tif', virtualFile, options=translateoptions)

stacking(dir_path)
