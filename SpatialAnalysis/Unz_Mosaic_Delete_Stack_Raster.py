## Beaware that this code will delete any zipfile in the Downloads folder.
## You should cut and paste any file in the Downloads folder that is not your downloaded imagery.

import os
import zipfile
import glob

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

#...............................................................................
# Search for zipfiles containing TIFF files and unzip their contants. 
def unzipFiles(path):
    # Search for zipfiles 
    files = glob.glob(path+'/*.zip')
    if len(files) != 0:
        counter = 1
        for file in files:
            zip_file = zipfile.ZipFile(file)
            fNames = zip_file.namelist()
            fName = fNames[0].rsplit(".")[1]

            zipinfos = zip_file.infolist()
            for zipinfo in zipinfos:
                # Search for raster (here TIFF) fiels
                zipinfo.filename = fName+'_'+str(counter)+'.tif'
                zip_file.extract(zipinfo, path+'/'+fName)
                    
            counter+=1
            zip_file.close()
            os.remove(file)
        print('All files have been unzipped')
    else:
        print('There is no zipfile')

unzipFiles(dir_path)
#...............................................................................

#...............................................................................
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
            print('Working on files in folder: ' + folder)

            # Output mosaic file
            out_fp = os.path.join(path, folder + '.tif')
            print('Output mosaic file will be saved as ' + out_fp)

            search_criteria = "*.tif"
            q = os.path.join(path, folder, search_criteria)
            print(q)

            image_files = glob.glob(q)

            # Iterate over raster files and add them to source -list in 'read mode'
            src_files_to_mosaic = []
            for f in image_files:
                src = rasterio.open(f)
                src_files_to_mosaic.append(src)

            # merge all rasters into one file
            mosaic, out_trans = merge(src_files_to_mosaic)

            # Copy the metadata
            out_meta = src.meta.copy()
            print('Metadat: ' + out_meta)

            # Update the metadata
            out_meta.update({"driver": "GTiff",
                             'dtype': 'float64',
                             "height": mosaic.shape[1],
                             "width": mosaic.shape[2],
                             "transform": out_trans,
                             "crs": "+proj=nzmg +lat_0=-41 +lon_0=173 +x_0=2510000 +y_0=6023150 +ellps=intl +towgs84=59.47,-5.04,187.44,0.47,-0.1,1.024,-4.5993 +units=m +no_defs "
                             }
                            )

            # Write the mosaic raster to disk
            with rasterio.open(out_fp, "w", **out_meta) as dest:
                dest.write(mosaic)

            # Compress the raster file into a new file and delete the old one
            translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine("-of Gtiff -co COMPRESS=LZW"))
            compressed = os.path.join(path, folder + '_Compressed.tif')
            gdal.Translate(compressed, out_fp, options=translateoptions)
            os.remove(out_fp)

##            # Remove all pieces of raster files
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

#...............................................................................

#...............................................................................
import glob
from osgeo import gdal

def stacking(path):
    bandPaths = glob.glob(path+'/*.tif')
    bandPaths.sort()

    virtualFile = gdal.BuildVRT("", bandPaths, separate=True)
    stackedImage = gdal.Translate(path+'/Multi_band.tif', virtualFile)

##stacking('C:/Users/saeed/Downloads')
