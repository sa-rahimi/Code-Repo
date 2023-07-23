import numba
from numba import jit
from numba import cuda
import numpy as np
from timeit import default_timer as timer
import math

# To run on CPU
def func1(x):
    for i in range(10000000):
        x[i] = math.sqrt(x[i] + 1) * x[-i]


# To run on GPU
@jit
def func2(x):
    for i in range(10000000):
        x[i] = math.sqrt(x[i] + 1) * x[-i]


if __name__=="__main__":
    
    n = 10000000
    a = np.ones(n, dtype = np.float64)

    print(f'This is to compare the speed of CPU and GPU over a simple arithmetic calculation,',
          f'like 10 million repeatation of "math.sqrt(x[i] + 1) * x[-i]",',
          f'where "x" is a one dimentional array with 10 million items of type float64.',
          f'\n\nThis computation takes: ')
    
    start = timer()
    func1(a)
    print('    ', timer()-start, 'seconds, without GPU')
    
    start = timer()
    func2(a)
    cuda.profile_stop()
    print('    ', timer()-start, 'seconds, with 1 GPU')
