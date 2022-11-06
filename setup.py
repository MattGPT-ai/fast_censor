from distutils.core import setup
from Cython.Build import cythonize

# run with `python setup.py build_ext --inplace` to compile cython functions
setup(ext_modules=cythonize('profanity_check_calc.pyx'),
      include_dirs=[])
