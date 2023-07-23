import os
import glob
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
##from scipy.stats import norm
import csv


# Find the directory of this piece of code
dir_path = os.path.dirname(os.path.realpath(__file__))

# Search and read raster files
search_criteria = '*.tif'
q = os.path.join(dir_path, search_criteria)
raster_files = glob.glob(q)
raster_files.sort()

# Read a csv file that contains all thresholds to create fuzzzy functions (in this case only one csv file)
search_criteria = '*.csv'
q = os.path.join(dir_path, search_criteria)
fuzzy_file_dir = glob.glob(q)
fuzzy_file = open(fuzzy_file_dir[0])

titles = []
values = []
for i, line in enumerate(fuzzy_file):
    line = line.strip()
    line = line.split(',')
    if i == 0:
        for j, title in enumerate(line):
            titles.append(title)
    else:
        vals = []
        for k, val in enumerate(line):
            vals.append(val)
            
        values.append(vals)

# Create a dictonary of fuzzy thresholds (min, mean, and max) for all each criterion
lst_dictionaries = []
n_fuzzy_class = int(len(values)/2)
for i, item in enumerate(titles):
    
    if i > 0:
        lst_predictors = []
        for j in range(n_fuzzy_class):
            k = int(j + (n_fuzzy_class) - 1)
            ave = float(values[j][i])
            std = float(values[k][i])
            low = ave - std
            up = ave + std
            diction = {'Predictor': item,
                'Class': values[j][0],
                'Ave': ave,
                'StD': std,
                'Low': low,
                'Up': up}
            lst_predictors.append(diction)
        sorted_lst = sorted(lst_predictors, key = lambda i: i['Ave'])
        lst_dictionaries.append(sorted_lst)

# Do the raster calculation with different fuzzy functions responding to different rasters and classes
for i, predictor in enumerate(lst_dictionaries):
    with rio.open(raster_files[i]) as src:
        meta = src.meta.copy()
        raster = src.read(1, masked=True)
    
    raster_name = os.path.basename(raster_files[i]).split('.')[0]
    print('The ' + raster_name + ' has been read')
   
    for j, item in enumerate(predictor):
        f_rest = ''
        out_GeoTiff = ''
        if j == 0:
            print('Raster calculation is in progress. \n This is the first Fuzzy class with lower bound: ' + str(item['Low'])
                  + ' , middle bound (highest membership): ' + str(item['Ave']) + ' , and upper bound: ' + str(item['Up']))
            print(str(item['Ave']))
            print(str(item['StD']))
            check1 = np.logical_and(raster < item['Ave'], raster < item['Ave'])
            check2 = np.logical_and(raster >= item['Ave'], raster <= item['Up'])
            f_res = np.where(check2, ((item['StD'] - abs(raster - item['Ave'])) / item['StD']), 0)
            f_res = np.where(raster > -9999, (f_res + check1), raster)
##            # This is the fuzzy function for the first class
##            f_res = (raster < item['Ave']) + (((item['StD'] - abs(((raster >= item['Ave'] and raster <= item['Up']) * raster) - item['Ave']))
##                                               / item['StD'] * (raster >= item['Ave'] and raster <= item['Up'])))

            out_GeoTiff = os.path.join(dir_path, 'Res', raster_name + '_' + item['Class'] + '.tif')

    
        elif j == (len(predictor)-1):
            print('Raster calculation is in progress. \n This is the last Fuzzy class with lower bound: ' + str(item['Low'])
                  + ' , middle bound (highest membership): ' + str(item['Ave']) + ' , and upper bound: ' + str(item['Up']))
            check1 = np.logical_and(raster >= item['Ave'], raster >= item['Ave'])
            check2 = np.logical_and(raster >= item['Low'], raster <= item['Ave'])
            f_res = np.where(check2, ((item['StD'] - abs(raster - item['Ave'])) / item['StD']), 0)
            f_res = np.where(raster > -9999, (f_res + check1), raster)
##            # This is the fuzzy function for the last class
##            f_res = (raster >= item['Ave']) + (((item['StD'] - abs(((raster >= item['Low'] and raster <= item['Ave']) * raster) - item['Ave']))
##                                                / item['StD']) * (raster >= item['Low'] and raster <= item['Ave'] ))
            out_GeoTiff = os.path.join(dir_path, 'Res', raster_name + '_' + item['Class'] + '.tif')
            
        else:
            print('Raster calculation is in progress. \n This is one of the middle Fuzzy class with lower bound: ' + str(item['Low'])
                  + ' , middle bound (highest membership): ' + str(item['Ave']) + ' , and upper bound: ' + str(item['Up']))
            check1 = np.logical_and(raster >= item['Low'], raster <= item['Up'])
            f_res = np.where(check1, ((item['StD'] - abs(raster - item['Ave'])) / item['StD']), 0)
            f_res = np.where(raster > -9999, f_res, raster)
##            # This is the fuzzy function for all middle classes
##            f_res = (raster >= item['Low'] and raster <= item['Up']) * ((item['StD'] - abs(((raster >= item['Low'] and raster <= item['Up'])
##                                                                                            * raster) - item['Ave'])) / item['StD'])
            out_GeoTiff = os.path.join(dir_path, 'Res', raster_name + '_' + item['Class'] + '.tif')

        print('Compressing and writing the results')
        with rio.open(out_GeoTiff, 'w', **meta, COMPRESS='LZW') as dest:
                dest.write(f_res, 1)
        print('Raster file ' + raster_name + ' has been created')


##for idx, raster_file in enumerate(raster_files):
##    # Read the first raster file from the first folder
##    print('Reading the first raster')
##    with rio.open(raster_file) as src:
##        meta = src.meta.copy()
##        raster = src.read(1, masked=True)
##    print('The raaster has been read')
##
##    fname = os.path.basename(raster_file)
##    print(fname)

##    print('Raster Calculation is in progress')
##    f_res = (f1 + f2) / 2
##    print('Raster Calculation has finished')
##
##    fname = os.path.basename(dir_to_f1)
##    out_GeoTiff = os.path.join(dir_path, 'Summer_20_21', fname)
##    print(out_GeoTiff)
##
##    print('Compressing and writing the results')
##    with rio.open(out_GeoTiff, 'w', **meta, COMPRESS='LZW') as dest:
##            dest.write(f_res, 1)
##    print('Raster file ' + fname + ' has been created')


##### Plot between -10 and 10 with .001 steps.
####x_axis = np.arange(0, 1120, 0.001)
##### Mean = 0, SD = 2.
####plt.plot(x_axis, norm.pdf(x_axis,559,187))
####plt.show()
