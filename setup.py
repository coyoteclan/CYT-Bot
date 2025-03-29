# filepath: /mnt/localdrive/ddd/bot/setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("shared.pyx", language_level="3")
)