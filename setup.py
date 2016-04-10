from distutils.core import setup

NAME = "duka"
VERSION = '0.1'

setup(
    name=NAME,
    packages=[NAME],
    version=VERSION,
    description='Dukascopy Bank SA historical data downloader',
    author='Giuseppe Pes',
    author_email='giuse88@gmail.com',
    url='https://github.com/giuse88/dukascopy-data-downloader',
    download_url='https://github.com/peterldowns/mypackage/tarball/' + VERSION,
    keywords=['dukascopy', 'forex', 'finance', 'historical data', 'price', 'currency'],
    classifiers=[],
)
