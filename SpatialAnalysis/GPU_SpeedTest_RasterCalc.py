import os
import glob
import rasterio as rio
import numba
from numba import jit
from numba import cuda
from timeit import default_timer as timer
import math


def raster_calculate_cpu(raster):
    f_res = ((raster * raster) / math.sqrt(raster.max())) * raster.mean()
    return f_res

@jit 
def raster_calculate_gpu(raster):        
    f_res = ((raster * raster) / math.sqrt(raster.max())) * raster.mean()
    return f_res

if __name__ == '__main__':
    # Find the directory of this piece of code
    dir_path = os.path.dirname(os.path.realpath(__file__))

    r_dir = os.path.join(dir_path, 'ras_lyr_1.tif')
    with rio.open(r_dir) as src:
        meta = src.meta.copy()
        f1 = src.read(1, masked=True)
        
    print(f'This is to compare the speed of CPU and GPU over a normall raster calculation,',
          f'like "((raster * raster) / math.sqrt(raster.max())) * raster.mean()",',
          f'on a raster file with "{f1.shape[0]}" rows and "{f1.shape[1]}" columns.',
          f'\n\nThis computation takes: ')
    
    start = timer()
    raster_calculate_cpu(f1)
    print('    ', timer()-start, 'seconds, without GPU')

    start = timer()
    raster_calculate_gpu(f1)
    cuda.profile_stop()
    print('    ', timer()-start, 'seconds, with 1 GPU')
    

        
