import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pylog import *

@pylog
def pl_add(a, b):

    a = np.empty([3,5,7], float)
    return c


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_add(a, b)
    print(c)