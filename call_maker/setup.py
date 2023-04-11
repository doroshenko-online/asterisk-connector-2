from os.path import join, dirname
from setuptools import setup, find_packages

setup(
    name='call-maker',
    version='0.1',
    package_dir={'call_maker': 'call_maker'},
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='dimad',
    include_package_data=True
)