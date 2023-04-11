from os.path import join, dirname
from setuptools import setup, find_packages

setup(
    name='ami-parser',
    version='0.1',
    package_dir={'ami_parser': 'ami_parser'},
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='dimad',
    include_package_data=True
)