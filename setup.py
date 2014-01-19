from distutils.core import setup

setup(name='PyBIND',
      version='0.1.0',
      description='Python package for writing ISC BIND files',
      author='Brian L. Brush',
      author_email='rhubarbsin@gmail.com',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Internet :: Name Service (DNS)']
      license='LICENSE',
      url='https://github.com/RhubarbSin/PyBIND',
      packages=['pybind'],
      install_requires=['ipaddr >= 2.1.7'])
