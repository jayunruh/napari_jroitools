# -*- coding: utf-8 -*-
"""
Created on Tues Jan 26 2021
License is GNU GPLv2
@author: Jay Unruh
"""
from napari_plugin_engine import napari_hook_implementation
import importroi
import numpy as np
import os

def roi_file_reader(path):
    decoder=importroi.RoiDecoder()
    if(path.endswith('.zip')):
        rois=decoder.readzip(path)
    else:
        rois=[decoder.readroi(path)]
    rtype=rois[0].getType()
    if(rtype=='rect'): rtype='rectangle'
    thickness=rois[0].thickness
    rois2=[rois[i].getNapariArray() for i in range(len(rois))]
    if(rtype=='point'):
        params={
            "name":os.path.basename(path),
            "edge_color":'red',
            "edge_width": thickness,
            "opacity": 0.3,
        }
        return [(rois2,params,'points')]
    else:
        params={
            "name":os.path.basename(path),
            "shape_type":rtype,
            "edge_color":'red',
            "edge_width": thickness,
            "opacity": 0.3,
        }
        return [(rois2,params,'shapes')]
    
@napari_hook_implementation
def napari_get_reader(path):
    if isinstance(path,str) and (path.lower().endswith('.zip') or path.lower().endswith('.roi')):
        return roi_file_reader
    return None