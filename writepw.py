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
    return imwrite(path,xValues,yValues,xLabel,yLabel,limits,logs)

def pwwrite(path,xValues,yValues,xLabel='x',yLabel='y',limits=None,logs=None):
    f=open(path,'wb')
    writestring(f,'pw2_file_type')
    f.write(struct.pack('i',0))
    writestring(f,xLabel)
    writestring(f,yLabel)
    f.write(struct.pack('i',yValues.shape[0]))
    f.write(struct.pack('i',yValues.shape[1]))
    if(xValues==None):
        xValues=[]
        for i in range(0,yValues.shape[0]): 
            xValues.append(np.arange(1,yValues.shape[1]+1,1,dtype='float32'))
        xValues=np.asfarray(xValues,dtype='float32')
    if(limits==None):
        limits=[0,0,0,0]
        limits[0]=np.amin(xValues)
        limits[1]=np.amax(xValues)
        limits[2]=np.amin(yValues)
        limits[3]=np.amax(yValues)
    lim_array=array.array('f',limits)
    lim_array.tofile(f)
    if(logs==None):
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
    if(logs==None):
        logs=[False,False,False]
    if(logs[0]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[1]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    if(logs[2]): f.write(struct.pack('i',1)) 
    else: f.write(struct.pack('i',0))
    for i in range(len(zValues)):
        f.write(struct.pack('i',len(zValues[i]))
        f.write(struct.pack('i',0))
        f.write(struct.pack('i',i%8))
        f.write(np.asfarray(xValues[i],dtype='float32').tobytes())
        f.write(np.asfarray(yValues[i],dtype='float32').tobytes())
        f.write(np.asfarray(zValues[i],dtype='float32').tobytes())
    f.write(struct.pack('i',0))
    f.close()
    
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
    f.write(str1)