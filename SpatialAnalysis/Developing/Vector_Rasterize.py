import os
import glob
import rtree
import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import gdalconst
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import time
import xarray as xr
from geocube.api.core import make_geocube

def rasterize(data, vec_dir, outFile):
    dataSrc = gdal.Open(data)
    import ogr
    shp = ogr.Open(vectorSrc)

    lyr = shp.GetLayer()

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(
        outFile,
        dataSrc.RasterXSize,
        dataSrc.RasterYSize,
        1,
        gdal.GDT_UInt16)
    dst_ds.SetGeoTransform(dataSrc.GetGeoTransform())
    dst_ds.SetProjection(dataSrc.GetProjection())
    if field is None:
        gdal.RasterizeLayer(dst_ds, [1], lyr, None)
    else:
        OPTIONS = ['ATTRIBUTE=' + field]
        gdal.RasterizeLayer(dst_ds, [1], lyr, None, options=OPTIONS)

    data, dst_ds, shp, lyr = None, None, None, None
    return outFile

if __name__ == '__main__':
    start_time = time.ctime()
    print("\nThe program started at: ", start_time)
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    search_criteria = 'raster.tif'
    raster_dir = os.path.join(dir_path, search_criteria)

    search_criteria = 'chunk_10_1.shp'
    vec_dir = os.path.join(dir_path, search_criteria)

    temp = rasterize(data, vec_dir, outFile)
##    vec_lyr = gpd.read_file(vec_dir)
##    print ('\nBase shapefile has been successfuly loaded')
##    vec_lyr['value'] = 1
##
##    print('\nRasterizing ...')
##    out_grid = make_geocube(
##        vector_data=vec_lyr,
##        measurements=["value"],
##        resolution=(-1, 1),
##        fill=-9999)

##    print('\nSaving the raster ...')
##    out_grid.rio.to_raster('./vegitation_1m.tif')
    
    end_time = time.ctime()
    print('\nThe program started at: ', end_time)
    print('\nDuane: I love you and I am in your service Land and Water Science')





data = gdal.Open(ndsm, gdalconst.GA_ReadOnly)
geo_transform = data.GetGeoTransform()
#source_layer = data.GetLayer()
x_min = geo_transform[0]
y_max = geo_transform[3]
x_max = x_min + geo_transform[1] * data.RasterXSize
y_min = y_max + geo_transform[5] * data.RasterYSize
x_res = data.RasterXSize
y_res = data.RasterYSize
mb_v = ogr.Open(shp)
mb_l = mb_v.GetLayer()
pixel_width = geo_transform[1]
output = '/home/zeito/pyqgis_data/my.tif'
target_ds = gdal.GetDriverByName('GTiff').Create(output, x_res, y_res, 1, gdal.GDT_Byte)
target_ds.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))
band = target_ds.GetRasterBand(1)
NoData_value = -999999
band.SetNoDataValue(NoData_value)
band.FlushCache()
gdal.RasterizeLayer(target_ds, [1], mb_l, options=["ATTRIBUTE=hedgerow"])

target_ds = None
