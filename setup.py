#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages

def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()

setup(
    name='napari_jroitools',
    version='0.0.9',
    author='Jay Unruh',
    description='A plugin to read and write ImageJ roi files into a napari shapes or points layer.',
    url='https://github.com/jayunruh/napari_jroitools',
    license='GNU GPLv2',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=["napari_plugin_engine>=0.1.4","numpy","numba"],
    py_modules=['napari_jroireader','importroi','napari_jroiwriter','exportroi','profiler','writepw','importpw'],
    entry_points={
        'napari.plugin': [
            'napari_jroireader = napari_jroireader',
            'napari_jroiwriter = napari_jroiwriter',
        ],
    },
)
