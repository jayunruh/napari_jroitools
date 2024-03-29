# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 16:15:45 2014

@author: jru
"""

import struct
import array
import numpy as np

def writePW4(path,xValues,yValues,xLabel='x',yLabel='y',limits=None,logs=None):
    #a more reasonable function name
    return pwwrite(path,xValues,yValues,xLabel,yLabel,limits,logs)

def pwwrite(path,xValues,yValues,xLabel='x',yLabel='y',limits=None,logs=None):
    f=open(path,'wb')
    writestring(f,'pw2_file_type')
    f.write(struct.pack('i',0))
    writestring(f,xLabel)
    writestring(f,yLabel)
    f.write(struct.pack('i',yValues.shape[0]))
    f.write(struct.pack('i',yValues.shape[1]))
    if(xValues is None):
        xValues=[]
        for i in range(0,yValues.shape[0]): 
            xValues.append(np.arange(1,yValues.shape[1]+1,1,dtype='float32'))
        xValues=np.asfarray(xValues,dtype='float32')
    if(limits is None):
        limits=[0,0,0,0]
        limits[0]=np.amin(xValues)
        limits[1]=np.amax(xValues)
        limits[2]=np.amin(yValues)
        limits[3]=np.amax(yValues)
    lim_array=array.array('f',limits)
    lim_array.tofile(f)
    if(logs is None):
        logs=[False,False]
    if(logs[0]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[1]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    for i in range(0,yValues.shape[0]):
        f.write(struct.pack('i',yValues.shape[1]))
        f.write(struct.pack('i',0))
        f.write(struct.pack('i',i%8))
        f.write(np.asfarray(xValues[i],dtype='float32').tobytes())
        f.write(np.asfarray(yValues[i],dtype='float32').tobytes())
    f.write(struct.pack('i',0))
    f.close()
    
def write3DTraj(path,xValues,yValues,zValues,xLabel='x',yLabel='y',zLabel='z',limits=None,logs=None):
    f=open(path,'wb')
    writestring(f,'pw2_file_type')
    f.write(struct.pack('i',2))
    writestring(f,xLabel)
    writestring(f,yLabel)
    writestring(f,zLabel)
    f.write(struct.pack('i',len(zValues)))
    #need to find out the max number of points
    maxpts=max([len(zValues[i]) for i in range(len(zValues[i]))])
    f.write(struct.pack('i',maxpts))
    if(limits is None):
        limits[0]=np.amin(xValues)
        limits[1]=np.amax(xValues)
        limits[2]=np.amin(yValues)
        limits[3]=np.amax(yValues)
        limits[4]=np.amin(zValues)
        limits[5]=np.amax(zValues)
    lim_array=array.array('f',limits)
    lim_array.tofile(f)
    if(logs is None):
        logs=[False,False,False]
    if(logs[0]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[1]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[2]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    for i in range(len(zValues)):
        f.write(struct.pack('i',len(zValues[i])))
        f.write(struct.pack('i',0))
        f.write(struct.pack('i',i%8))
        f.write(np.asfarray(xValues[i],dtype='float32').tobytes())
        f.write(np.asfarray(yValues[i],dtype='float32').tobytes())
        f.write(np.asfarray(zValues[i],dtype='float32').tobytes())
    f.write(struct.pack('i',0))
    f.close()
    
def write2DHist(path,xValues,yValues,xLabel='x',yLabel='y',limits=None,logs=None,binSize=1):
    f=open(path,'wb')
    writestring(f,'pw2_file_type')
    f.write(struct.pack('i',4))
    writestring(f,xLabel)
    writestring(f,yLabel)
    #f.write(struct.pack('i',yValues.shape[0]))
    #f.write(struct.pack('i',yValues.shape[1]))
    if(limits==None or len(limits)<6):
        limits=[0,0,0,0,0,0]
        limits[0]=np.amin(xValues)
        limits[1]=np.amax(xValues)
        limits[2]=np.amin(yValues)
        limits[3]=np.amax(yValues)
        limits[4]=0.0
        limits[5]=1.0
    lim_array=array.array('f',limits)
    lim_array.tofile(f)
    if(logs==None):
        logs=[False,False]
    if(logs[0]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[1]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    f.write(struct.pack('i',6))
    f.write(struct.pack('i',binSize))
    #write the lut
    f.write(getNiceLut().tobytes())
    f.write(struct.pack('i',len(yValues)))
    f.write(np.asfarray(xValues,dtype='float32').tobytes())
    f.write(np.asfarray(yValues,dtype='float32').tobytes())
    f.close()
    
def getNiceLut(whiteback=True):
    r=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]
    g=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,251,247,243,239,235,231,227,223,219,215,211,207,203,199,195,191,187,183,179,175,171,167,163,159,155,151,147,143,139,135,131,127,123,119,115,111,107,103,99,95,91,87,83,79,75,71,67,63,59,55,51,47,43,39,35,31,27,23,19,15,11,7,3,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,255]
    b=[0,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,251,247,243,239,235,231,227,223,219,215,211,207,203,199,195,191,187,183,179,175,171,167,163,159,155,151,147,143,139,135,131,127,123,119,115,111,107,103,99,95,91,87,83,79,75,71,67,63,59,55,51,47,43,39,35,31,27,23,19,15,11,7,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,255]
    if(whiteback):
        r[0]=255
        r[255]=255
        g[0]=255
        g[255]=120
        b[0]=255
        b[255]=120
    return np.array(list(zip(b,g,r,[255]*256)),dtype=np.uint8).flatten()
    
def writerawfloat(path,arr):
    #use swapaxes to change array order if necessary
    f=open(path,'wb')
    for i in range(0,arr.shape[0]):
        arr2=arr[i]
        if(arr[i].ndim>1): arr2=np.reshape(arr[i],-1)
        f.write(np.asfarray(arr2,dtype='float32').tobytes())
    f.close();
    
def writestring(f,str1):
    f.write(struct.pack('i',len(str1)))
    f.write(bytes(str1,'utf-8'))