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

gdal.PushErrorHandler('CPLQuietErrorHandler')

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
    

def zonal_stats(r_array, v_lyr, r_gt, x_size, y_size):
    mem_drv = ogr.GetDriverByName('Memory')
    driver = gdal.GetDriverByName('MEM')

    # Loop through vectors
    stats = []
    feat = v_lyr.GetNextFeature()
    while feat is not None:

        # Create a temporary vector layer in memory
        mem_ds = mem_drv.CreateDataSource('out')
        mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
        mem_layer.CreateFeature(feat.Clone())

        # Rasterize it
        r_vds = driver.Create('', x_size, y_size, 1, gdal.GDT_Byte)
        r_vds.SetGeoTransform(r_gt)
        gdal.RasterizeLayer(r_vds, [1], mem_layer)#,burn_values=[1])
        rv_band = r_vds.GetRasterBand(1)
        rv_band.SetNoDataValue(-9999)
        rv_array = r_vds.ReadAsArray()
        rv_masked = np.ma.MaskedArray(rv_array, mask=r_array == -9999)

        # Mask the source data array with our current feature
        # we take the logical_not to flip 0<->1 to get the correct mask effect
        # we also mask out nodata values explictly
        masked = np.ma.MaskedArray(
            r_array,
            mask=np.logical_or(np.logical_or(r_array == no_data, r_array == 0),
                np.logical_not(rv_masked)
            )
        )

        # Depending on what you want to do with the raster
        # Here we need to calculate 25 and 75 percentiles
        # So, it seems reasonable to compress the array
        compressed = masked.compressed()
        
        f_id = int(feat.GetField('fid'))
        f_dn = int(feat.GetField('DN'))
        f_count = int(masked.count())
        f_min = float(masked.min())
        f_max = float(masked.max())
        f_mean = float(np.ma.mean(compressed))
        f_median = float(np.ma.median(compressed))
        f_std = float(compressed.std())
        f_cv = None
        if f_mean != 0:
            f_cv = float((f_std / f_mean) * 100)        
        f_q25 = float(np.nanpercentile(compressed, 25))
        f_q75 = float(np.nanpercentile(compressed, 75))
        
        feature_stats = []
        feature_stats.extend([
            f_id,
            f_dn,
            f_count,
            f_min,
            f_max,
            f_mean,
            f_median,
            f_std,
            f_cv,
            f_q25,
            f_q75
        ])

        stats.append(feature_stats)
        r_vds = None
        mem_ds = None
        rv_array = []
        rv_masked = []
        feat = v_lyr.GetNextFeature()

    return stats


if __name__ == "__main__":

    start_time = time.ctime()
    print("\nThe program started at: ", start_time)

    # Read the input vector layer
    search_criteria = 'V_Temp.shp'
    v_dir = os.path.join(dir_path, search_criteria)
    v_open = ogr.Open(v_dir)
    v_lyr = v_open.GetLayer(0)
    assert(v_lyr)
    print ('\nShapefile has been successfuly loaded')

    # Read the input raster layer
    search_criteria = 'R_Temp_5.tif'
    r_dir = os.path.join(dir_path, search_criteria)
    r_lyr = gdal.Open(r_dir, GA_ReadOnly)
    assert(r_lyr)
    print ('\nRaster file has been successfuly loaded')

    # Read the raster file as an array to pass it on to the function
    r_gt = r_lyr.GetGeoTransform()
    r_band = r_lyr.GetRasterBand(1)
    r_band.SetNoDataValue(float(-9999))
    r_array = r_band.ReadAsArray()

    stats = zonal_stats(r_array, v_lyr, r_gt, int(r_band.XSize), int(r_band.YSize))
    stats = pd.DataFrame(stats)
    out_csv = os.path.join(dir_path, 'Temp.csv')
    stats.to_csv(out_csv)
    
    
    end_time = time.ctime()
    print("\nThe program finished at: ", end_time)
