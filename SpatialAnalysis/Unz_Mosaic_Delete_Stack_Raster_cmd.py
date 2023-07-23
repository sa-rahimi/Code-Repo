## Beaware that this code will delete any zipfile in the Downloads folder.
## You should cut and paste any file in the Downloads folder that is not your downloaded imagery.

import os
import zipfile
import glob

dir_path = os.path.dirname(os.path.realpath(__file__))

def unzipFiles(path):
    files = glob.glob(path+'/*.zip')
    if len(files) != 0:
        counter = 1
        for file in files:
            zip_file = zipfile.ZipFile(file)
            fNames = zip_file.namelist()
            fName = fNames[0].rsplit(".")[1]

            zipinfos = zip_file.infolist()
            for zipinfo in zipinfos:
                zipinfo.filename = fName+'_'+str(counter)+'.tif'
                zip_file.extract(zipinfo, path+'/'+fName)
                    
            counter+=1
            zip_file.close()
            os.remove(file)
        print('All files have been unzipped')
    else:
        print('There is no zip file')

## You need to change the path to your own directory where you have stored your downloaded zipped files
unzipFiles(dir_path)

## Use the binary file to install rasterio and gdal using the following code:
    ## (python.exe -m pip install C:/Users/saeed/Downloads/rasterio-1.2.6-cp39-cp39-win_amd64.whl)
        ## See "https://rasterio.readthedocs.io/en/latest/installation.html" for more details
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

def mosaic(path):
    folders = os.listdir(path)
    print(folders)
    for folder in folders:
        if os.path.isdir(folder):
            print('Working on Band_' + folder)
            files_to_mosaic = glob.glob(path+'/'+folder+'/*.tif')

            files_string = " ".join(files_to_mosaic)

            command = 'gdal_merge.py -o ' + path + '/' + folder + '.tif -of gtiff ' + files_string
            print(os.popen(command).read())
            print(command)

            
##            for file in files_to_mosaic:
##                os.remove(file)
##            import shutil
##            dir = os.path.join(path, folder)
##            print('Image ' + folder + '.tif has been created and folder ' + folder + ' has been deleteed.')
##            shutil.rmtree(dir)
            print('Band_' + folder + ' is finished')
        else:
            print('There is no folder containing TIFF files')

mosaic(dir_path)
##
##import glob
##from osgeo import gdal
##
##def stacking(path):
##    bandPaths = glob.glob(path+'/*.tif')
##    bandPaths.sort()
##
##    virtualFile = gdal.BuildVRT("", bandPaths, separate=True)
##    stackedImage = gdal.Translate(path+'/Multi_band.tif', virtualFile)
##
##stacking('C:/Users/saeed/Downloads')
