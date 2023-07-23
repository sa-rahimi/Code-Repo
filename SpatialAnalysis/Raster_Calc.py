import os
import glob
import rasterio as rio

# Find the directory of this piece of code
dir_path = os.path.dirname(os.path.realpath(__file__))

# Search and read raster files (in this casse from two different folders)
search_criteria = '*.tif'

dir1 = os.path.join(dir_path, 'Summer_2020')
q = os.path.join(dir1, search_criteria)
dir1_files = glob.glob(q)
dir1_files.sort()

dir2 = os.path.join(dir_path, 'Summer_2021')
q = os.path.join(dir2, search_criteria)
dir2_files = glob.glob(q)
dir2_files.sort()


for idx, dir_to_f1 in enumerate(dir1_files):
    # Read the first raster file from the first folder
    print('Reading the first raster')
    with rio.open(dir_to_f1) as src:
        meta = src.meta.copy()
        print(meta)
        f1 = src.read(1, masked=True)
    print('First raaster has been read')

    # Read the first raster file from the second folder
    print('Reading the second raster')
    dir_to_f2 = dir2_files[idx]
    with rio.open(dir_to_f2) as src:
        f2 = src.read(1, masked=True)
    print('Second raaster has been read')

    print('Raster Calculation is in progress')
    f_res = (f1 + f2) / 2
    print('Raster Calculation has finished')

    fname = os.path.basename(dir_to_f1)
    out_GeoTiff = os.path.join(dir_path, 'Summer_20_21', fname)
    print(out_GeoTiff)

    print('Compressing and writing the results')
    with rio.open(out_GeoTiff, 'w', **meta, COMPRESS='LZW') as dest:
            dest.write(f_res, 1)
    print('Raster file ' + fname + ' has been created')




