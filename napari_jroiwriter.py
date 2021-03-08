# -*- coding: utf-8 -*-
"""
Created on Tues Jan 26 2021
License is GNU GPLv2
@author: Jay Unruh
"""
from napari_plugin_engine import napari_hook_implementation
import exportroi
import importroi
import numpy as np
import os

def roi_file_writer(path,data,meta,layer_type):
    #layer_data is data,meta,layer_type
    #decoder=importroi.RoiDecoder()
    encoder=exportroi.RoiEncoder()
    layer_data=[data,meta,layer_type]
    rois=exportroi.get_rois_from_data(layer_data)
    if(rois is None):
        return None
    if(len(rois)<2):
        encoder.writeRoi(rois[0],path)
    else:
        encoder.writeMultiRois(rois,path)
    return path
    
@napari_hook_implementation
def napari_write_shapes(path,data,meta):
    if(path.lower().endswith('.roi') or path.lower().endswith('.zip')):
        return roi_file_writer(path,data,meta,'shapes')
    return None
    
@napari_hook_implementation
def napari_write_points(path,data,meta):
    if(path.lower().endswith('.roi') or path.lower().endswith('.zip')):
        return roi_file_writer(path,data,meta,'points')
    return None