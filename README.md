#this is the "readme" page for Jiawei_pylog_branch
  I modify some of the jinja templete to make it generate correct C/C++ template code.
  Also, the analysior and IPanalysior had been modified to make sure it get correct IP core. 


# PyLog

PyLog: An Algorithm-Centric FPGA Programming and Synthesis Flow

## Test Environment
 - Ubuntu 18.04.4 LTS
 - Python 3.6.9
 - FPGA Boards: [ZedBoard](http://zedboard.org/product/zedboard), [PYNQ](https://store.digilentinc.com/pynq-z1-python-productivity-for-zynq-7000-arm-fpga-soc/), [Ultra96](http://zedboard.org/product/ultra96)

## Getting Started

### Setting paths

Before running PyLog, please add the path to your PyLog directory to `PYTHONPATH`. You can add the following line into your `~/.bashrc` file:
```{bash}
export PYTHONPATH=/your/path/to/pylog:$PYTHONPATH
```

Also, please modify the paths at the beginning the following files: 
- `tests/env.py`: Modify PyLog path accordingly. `env.py` is imported by test code under `tests` (not necessary if you add PyLog path to `PYTHONPATH`)
- `pylog.py`: Set the following addresses for your host system (used for compilation and synthesis) and target system (used for deployment, i.e. the FPGA system)
  - `HOST_ADDR`: The address of the host system (should be reachable from target system), used only in `deploy` mode to fetch syntehsis results. 
  - `HOST_BASE`: The path to the workspace directory on the host system. If the directory doesn't exist, PyLog will create it. PyLog compilation and synthesis outputs will be written to this directory. 
  - `TARGET_ADDR`: The address of the target system. Currently not used. 
  - `TARGET_BASE`: The path to the workspace directory on the target system. If the directory doesn't exist, PyLog will create it. PyLog compilation outputs will be written to this directory. Bitstreams (\*.bit) and hardware handoff files (\*.hwh) will be copied to this directory from host system. 
  - `WORKSPACE`: The actually used path to workspace. Points to `HOST_BASE` when you are using PyLog for synthesis on the host system and `TARGET_BASE` when you are using PyLog for deployment on the target system.  

### PyLog usage
To use PyLog, import pylog and simply add PyLog decorator `@pylog` to the function that you'd like to synthesize into an FPGA accelerator. Pass NumPy arrays to the decorated function and call the decorated function. Then run the whole Python program. In the following example, `vecadd` function will be compiled into HLS C code by PyLog. 

```Python
import numpy as np
from pylog import *

@pylog
def vecadd(a, b, c):
    for i in range(1024):
        c[i] = a[i] + b[i]
    return 0

if __name__ == "__main__":
    length = 1024
    a = np.random.rand(length).astype(np.float32)
    b = np.random.rand(length).astype(np.float32)
    c = np.random.rand(length).astype(np.float32)
    
    vecadd(a, b, c)
```

You can also pass arguments to `@pylog` decorator to control the behavior of PyLog. The following arguments can be passed to `@pylog`: 

- `mode`: You can pass one of the following strings to control the action of PyLog. By default `mode='cgen'`.
  - `'cgen'` or `'codegen'`: Generates HLS C code only; 
  - `'hwgen'`: Generates HLS C code and call Vivado HLS and Vivado to generate hardware; 
  - `'pysim'`: Run the code with standard Python interpreter. You need to add `from pysim import *` in your code to use `pysim`; 
  - `'deploy'` or `'run'` or `'acc'`: Run PyLog in deploy mode. This will program FPGA, use PyLog runtime to invoke FPGA and collect results. 
  
- `path`: This overwrites the `WORKSPACE` string in `pylog.py`. 
- `board`: The target FPGA board. Currently PyLog support `zedboard`, `pynq`, and `ultra96`. By default `board='ultra96'`. 

Here is one example of configuring PyLog:  

```Python
@pylog(mode='deploy', board='pynq')
```
In this example, PyLog will run in deploy mode, targeting PYNQ board (implying the current program is running on a PYNQ board). 

## Tests

Example PyLog code can be found under `tests`. To run a test, simply run it as a regular Python script: 

```bash
python tests/matmul.py
```

