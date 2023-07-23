import os
import glob
import rasterio as rio
import csv

# You need to copy and paste this piece of code to the directory,
    # where you have stored your downloaded zipped files.
dir_path = os.path.dirname(os.path.realpath(__file__))

# Search and read raster files
search_criteria = "Temp.tif"
q = os.path.join(dir_path, search_criteria)

stacked_raster = rio.open(q)

raster_list = []
for band in range(1, stacked_raster.count + 1):
    raster = stacked_raster.read(band, masked=True)
    raster_list.append(raster)
print("Stack image has been converted to a list with ")
pixel_vals = []
for row in range(stacked_raster.height):
    for col in range(stacked_raster.width):
        pixel_val = ""
        for band in range(stacked_raster.count):
            if band != (stacked_raster.count - 1):
                pixel_val = pixel_val + str(round(raster_list[band][row][col], 1)) + "_"
            else:
                pixel_val = pixel_val + str(round(raster_list[band][row][col], 1))
                
        if pixel_val not in pixel_vals:
            pixel_vals.append(pixel_val)
    print(row)

file_name = "Unique_Pixel_Values1.csv"
csv_file = os.path.join(dir_path, file_name)

with open(csv_file, 'w') as f:
    # using csv.writer method from CSV package
    write = csv.writer(f)
    write.writerows(pixel_vals)
