# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 16:52:23 2021
License is GNU GPLv2
@author: Jay Unruh
"""

import numpy as np
import struct
import math
import array
import sys
import os
import importroi

class RoiEncoder():
    
    def __init__(self):
        self.HEADER_SIZE=64
        self.HEADER2_SIZE=64
        self.VERSION=228
        self.subPixelResolution=False
        #types
        self.polygon,self.rect,self.oval,self.line,self.freeline=0,1,2,3,4
        self.polyline,self.noRoi,self.freehand,self.traced,self.angle,self.point=5,6,7,8,9,10
        
    def writeMultiRois(self,rois,path):
        from zipfile import ZipFile
        zf=ZipFile(path,mode='w')
        for i in range(len(rois)):
            barr=self.getRoiBytes(rois[i])
            tname=rois[i].name
            if(tname is None):
                #tname='roi'+str(i+1)+'.roi'
                tname=rois[i].getStandardName()
            if not tname.endswith('.roi'):
                tname=tname+'.roi'
            zf.writestr(tname,barr.tobytes())
        return
        
    def writeRoi(self,roi,path):
        barr=self.getRoiBytes(roi)
        #finally write the byte array
        f=open(path,"wb")
        try:
            barr.tofile(f)
        finally:
            f.close()
        return

    def getRoiBytes(self,roi):
        r=roi.getBounds()
        self.subPixelResolution=roi.getSubPixelResolution()
        if(r[2]>65535 or r[3]>65535 or r[0]>65535 or r[1]>65535): self.subPixelResolution=True
        roiType=roi.getType()
        rtype=self.rect
        options=0
        roiName=roi.name
        if(roiName is not None):
            roiNameSize=len(roiName)*2
        else:
            roiNameSize=0
            
        #not sure why we didn't do this earlier
        rtype=roi.rtype
        n=0
        floatSize=0
        x,y,xf,yf=None,None,None,None
        if(rtype==self.polygon):
            n=len(roi.xcoords)
            x=roi.xcoords
            y=roi.ycoords
            if(self.subPixelResolution):
                xf=x
                yf=y
                floatSize=n*8
        
        roiDecoder=importroi.RoiDecoder()
        dataSize=self.HEADER_SIZE+self.HEADER2_SIZE+n*4+floatSize+roiNameSize
        barr=np.zeros(dataSize,dtype=np.ubyte)
        writeString(barr,0,'Iout')
        writeMotorolaShort(barr,roiDecoder.VERSION_OFFSET,self.VERSION)
        writeByte(barr,roiDecoder.TYPE,[rtype])
        writeMotorolaShort(barr,roiDecoder.VERSION_OFFSET,self.VERSION)
        writeMotorolaShort(barr,roiDecoder.TOP,[r[0],r[1],r[0]+r[2],r[1]+r[3]])
        if(self.subPixelResolution and (rtype==self.rect or rtype==self.oval)):
            if(len(roi.xcoords)==4):
                writeMotorolaFloat(barr,roiDecoder.XD,[roi.xcoords[0],roi.ycoords[0],r[0]+r[2],r[1]+r[3]])
                writeMotorolaShort(barr,roiDecoder.OPTIONS,roiDecoder.SUB_PIXEL_RESOLUTION)
        if(n>65535 and rtype!=self.point):
            #this ist a shape roi which isn't supported yet
            None
        if(rtype==self.point and n>65535):
            writeMotorolaInt(barr,roiDecoder.SIZE,n)
        else:
            writeMotorolaShort(barr,roiDecoder.N_COORDINATES,n)
        position=roi.position
        if(isinstance(roi.position,list)):
            position=roi.position[-1]
        if(roi.position is None):
            position=0
        writeMotorolaInt(barr,roiDecoder.POSITION,position)
        if(rtype==self.rect):
            #don't support rounded rectangles
            None
        if(rtype==self.line):
            writeMotorolaFloat(barr,roiDecoder.X1,[roi.xcoords[0],roi.ycoords[0],roi.xcoords[1],roi.ycoords[1]])
        if(rtype==self.point):
            writeByte(barr,roiDecoder.POINT_TYPE,0)
            writeMotorolaShort(barr,roiDecoder.STROKE_WIDTH,roi.thickness)
        if(self.VERSION>=218):
            self.saveStrokeWidthAndColor(barr,roiDecoder,roi.thickness)
        if(n>0):
            base1=64
            base2=base1+2*n
            writeMotorolaShort(barr,base1,x)
            writeMotorolaShort(barr,base2,y)
            if(xf is not None):
                base1=64+4*n
                base2=base1+2*n
                writeMotorolaFloat(barr,base1,xf)
                writeMotorolaFloat(barr,base2,yf)
        return barr
    
    def saveStrokeWidthAndColor(self,barr,roiDecoder,strokeWidth,strokeColor=None,fillColor=None):
        writeMotorolaShort(barr,roiDecoder.STROKE_WIDTH,strokeWidth)
        if(strokeColor is not None):
            writeMotorolaInt(barr,roiDecoder.STROKE_COLOR,strokeColor)
        if(fillColor is not None):
            writeMotorolaInt(barr,roiDecoder.FILL_COLOR,fillColor)
        return
                
def get_rois_from_data(layer_data):
    #this creates an array of roi objects from napari layer data
    roidata1=np.array(layer_data[0])
    nrois=roidata1.shape[0]
    rois=[]
    thickness=layer_data[1]['edge_width'][0]
    types=['polygon','rectangle','ellipse','line','freeline','path','noRoi','freehand','traced','angle','point']
    if(layer_data[2]=='shapes'):
        #this can be line, rectangle, ellipse, path, polygon
        #don't support rotated shapes for now
        stype=layer_data[1]['shape_type'][0]
        rtype=types.index(stype)
        for i in range(len(roidata1)):
            roidata=roidata1[i]
            ndims=len(roidata[0])
            if(ndims>2):
                position=roidata[0,-3]
            else:
                position=0
            troi=importroi.Roi(roidata[:,-1],roidata[:,-2],position=position,thickness=thickness,rtype=rtype)
            rois.append(troi)
    else:
        for i in range(len(roidata1)):
            roidata=roidata1[i]
            ndims=len(roidata[0])
            if(ndims>2):
                position=roidata[0,-3]
            else:
                position=0
            troi=importroi.Roi(roidata[:,-1],roidata[:,-2],position=position,rtype=10)
            rois.append(troi)
    return rois

def writeString(barr,offset,str1):
    str2=bytes(str1,'utf-8')
    strlen=len(str2)
    barr[offset:(offset+strlen)]=np.frombuffer(str2,dtype='uint8')
    return

def writeByte(barr,offset,vals):
    vals2=np.array(vals,dtype=np.ubyte)
    barr[offset:(offset+len(vals2))]=vals2

def writeMotorolaShort(barr,offset,vals):
    vals2=np.array(vals,dtype='>h').tobytes()
    barr[offset:(offset+len(vals2))]=np.frombuffer(vals2,dtype='uint8')
    return

def writeMotorolaInt(barr,offset,vals):
    vals2=np.array(vals,dtype='>i').tobytes()
    barr[offset:(offset+len(vals2))]=np.frombuffer(vals2,dtype='uint8')
    return

def writeMotorolaFloat(barr,offset,vals):
    vals2=np.array(vals,dtype='>f').tobytes()
    barr[offset:(offset+len(vals2))]=np.frombuffer(vals2,dtype='uint8')
    return

def makeTestRoi():
    return importroi.Roi([10,20],[10,20],position=0,rtype=3,name='test')