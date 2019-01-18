from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("pynita_source/nita_funs/distance_funs/distance_funs_cython.pyx", include_path=[numpy.get_include()])
)