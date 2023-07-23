import glob
import os

from osgeo import gdal
import numpy as np



for fn in filenames:
    ds = gdal.Open(fn, 1)                      # pass 1 to modify the raster
    n = ds.RasterCount                         # get number of bands
    for i in range(1, n+1):
        band = ds.GetRasterBand(i)
        arr = band.ReadAsArray()               # read band as numpy array
        arr = np.where(arr == -340282346638528859811704183484516925440.0, -9999, arr)  # change 0 to -9999
        band.WriteArray(arr)                   # write the new array
        band.SetNoDataValue(-9999)            # set the NoData value
        band.FlushCache()                      # save changes
    del ds

if __name__ == '__main__':


    # Find the directory of this piece of code
    dir_path = os.path.dirname(os.path.realpath(__file__))
	os.chdir(r'D:\LWS Projects\South Canterbury Catchment Collective\2 Working Files\Working Datasets\1 - Spatial Data\Hydrological Analysis\p')

filenames = glob.glob('*es.tif')