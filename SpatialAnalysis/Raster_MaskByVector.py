import fiona
import rasterio as rio
import rasterio.mask
import os
import glob
from timeit import default_timer as timer


if __name__ == '__main__':
    # Find the directory of this piece of code
    dir_path = os.path.dirname(os.path.realpath(__file__))

    
    v_dir = os.path.join(dir_path, 'Mask.shp')
    with fiona.open(v_dir, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    print('\n shapefile has been added')

    r_dir = os.path.join(dir_path, 'LCDB_5m.tif')
    with rio.open(r_dir) as src:
        out_image, out_transform = rio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    print('\n raster has been clipped')


    out_meta.update({"driver": "GTiff",
             "height": out_image.shape[1],
             "width": out_image.shape[2],
             "transform": out_transform})

    out_r_dir = os.path.join(dir_path, 'Clipped.tif')
    with rio.open(out_r_dir, "w", **out_meta) as dest:
        dest.write(out_image)
