import os
import zipfile
import glob

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

# Search for zipfiles containing TIFF files and unzip their contants. 
def unzipFiles(path):
    # Search for zipfiles
    search_criteria = '*.zip'
    q = os.path.join(path, search_criteria)
    files = glob.glob(q)
    
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
