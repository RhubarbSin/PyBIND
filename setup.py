"""
docstring
"""

__version__ = '$Revision$'
# $Source$

from distutils.core import setup

setup(name='pybind',
      version='0.5',
      description='Python module for writing BIND files',
      author='Brian L. Brush',
      author_email='rhubarbsin@gmail.com',
      classifiers=['License :: OSI Approved :: MIT License'],
      url='https://github.com/RhubarbSin/pybind',
      py_modules=['iscconf', 'bindconf', 'dnsrecord', 'dnszone'],
      )
