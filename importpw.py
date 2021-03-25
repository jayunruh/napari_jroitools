# -*- coding: utf-8 -*-
"""
Created on Wed Nov 05 17:06:35 2014

@author: jru
"""

import struct
import array
import math
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib as mpl
import numpy as npy

def gettype(path):
    #this gets the plot type: 0 is plot4, 3 is plothist, 4 is plot2dhist, 5 is plotcolumn
    f=open(path,"rb")
    try:
        xLabel=readstring(f)
        if xLabel=="pw2_file_type":
            id=struct.unpack('i',f.read(4))[0]
            xLabel=readstring(f)
        else:
            id=0
    finally:
        f.close()
    return id

def plot4read(path):
    #here we read a plot4 (id=0)
    f=open(path,"rb")
    try:
        xLabel=readstring(f)
        if xLabel=="pw2_file_type":
            id=struct.unpack('i',f.read(4))[0]
            xLabel=readstring(f)
        else:
            id=0
        if id!=0:
            return None
        yLabel=readstring(f)
        #print("xlab="+xLabel)
        #print("id="+str(id))
        nseries=struct.unpack('i',f.read(4))[0]
        maxpts=struct.unpack('i',f.read(4))[0]
        xMin=struct.unpack('f',f.read(4))[0]
        xMax=struct.unpack('f',f.read(4))[0]
        yMin=struct.unpack('f',f.read(4))[0]
        yMax=struct.unpack('f',f.read(4))[0]
        logx=struct.unpack('i',f.read(4))[0]==1
        logy=struct.unpack('i',f.read(4))[0]==1
        npts=[]
        xValues=[]
        yValues=[]
        shapes=[]
        colors=[]
        errs=[]
        annot=[]
        for i in range(0,nseries):
            npts.append(struct.unpack('i',f.read(4))[0])
            shapes.append(struct.unpack('i',f.read(4))[0])
            colors.append(struct.unpack('i',f.read(4))[0])
            #print("npts"+`i`+"="+`npts[i]`)
            xValues.append(readfltarray(f,npts[i]))
            yValues.append(readfltarray(f,npts[i]))
        #need to get the error bars here if present
        c=f.read(4)
        if c:
            showerrs=struct.unpack('i',c)[0]==1
        else:
            showerrs=0
        if showerrs:
            for i in range(0,nseries):
                #lower errs
                errs.append(readfltarray(f,npts[i]))
                #upper errs
                errs.append(readfltarray(f,npts[i]))
        #need to get annotations if present
        c=f.read(4)
        if c:
            annotated=struct.unpack('i',c)[0]==1
        else:
            annotated=0
        if annotated:
            for i in range(0,nseries):
                annot.append(readstring(f))
    finally:
        f.close()
    return xValues,yValues,xLabel,yLabel,[xMin,xMax,yMin,yMax],[logx,logy],colors,shapes,errs,annot

def plothistread(path):
    #here we read a plothist (id=3)
    f=open(path,"rb")
    try:
        xLabel=readstring(f)
        if xLabel=="pw2_file_type":
            id=struct.unpack('i',f.read(4))[0]
            xLabel=readstring(f)
        else:
            id=0
        if id!=3:
            return None
        yLabel=readstring(f)
        xMin=struct.unpack('f',f.read(4))[0]
        xMax=struct.unpack('f',f.read(4))[0]
        yMin=struct.unpack('f',f.read(4))[0]
        yMax=struct.unpack('f',f.read(4))[0]
        logx=struct.unpack('i',f.read(4))[0]==1
        logy=struct.unpack('i',f.read(4))[0]==1
        color=struct.unpack('i',f.read(4))[0]
        #note that this binsize is not in units
        binSize=struct.unpack('f',f.read(4))[0]
        npts=[]
        maxpts=struct.unpack('i',f.read(4))[0]
        npts.append(maxpts)
        xValues=readfltarray(f,maxpts)
    finally:
        f.close()
    #need to generate the histogram bins
    histSize=256
    newhistsize=int(histSize/binSize)
    histbins=[]
    if not logx:
        tbinsize=(binSize/float(histSize))*(xMax-xMin)
        for i in range(0,newhistsize):
            histbins.append(xMin+tbinsize*float(i))
    else:
        if xMin>0.0:
            logxmin=math.log(xMin)
        else:
            xMin=findmingt0(xValues,xMax)
            logxmin=math.log(xMin)
        logxmax=math.log(xMax)
        tbinsize=(binSize/histSize)*(logxmax-logxmin)
        for i in range(0,newhistsize):
            val=math.exp(logxmin+tbinsize*float(i))
            histbins.append(val)
    return xValues,histbins,xLabel,yLabel,[xMin,xMax,yMin,yMax],[logx,logy],color

def get1DHistBins(binSize,xMin,xMax,logx,logxmin):
    #need to generate the histogram bins
    histSize=256
    newhistsize=int(histSize/binSize)
    histbins=[]
    if not logxmin:
        logxmin=1.0
    if not logx:
        tbinsize=(binSize/float(histSize))*(xMax-xMin)
        for i in range(0,newhistsize):
            histbins.append(xMin+tbinsize*float(i))
    else:
        if xMin>0.0:
            logxmin=math.log(xMin)
        #else:
        #    xMin=findmingt0(xValues,xMax)
        #    logxmin=math.log(xMin)
        logxmax=math.log(xMax)
        tbinsize=(binSize/histSize)*(logxmax-logxmin)
        for i in range(0,newhistsize):
            val=math.exp(logxmin+tbinsize*float(i))
            histbins.append(val)
    return histbins
    
def plot2Dhistread(path):
    #here we read a plot2Dhist (id=4)
    f=open(path,"rb")
    try:
        xLabel=readstring(f)
        if xLabel=="pw2_file_type":
            id=struct.unpack('i',f.read(4))[0]
            xLabel=readstring(f)
        else:
            id=0
        if id!=4:
            return None
        yLabel=readstring(f)
        xMin=struct.unpack('f',f.read(4))[0]
        xMax=struct.unpack('f',f.read(4))[0]
        yMin=struct.unpack('f',f.read(4))[0]
        yMax=struct.unpack('f',f.read(4))[0]
        intMin=struct.unpack('f',f.read(4))[0]
        intMax=struct.unpack('f',f.read(4))[0]
        logx=struct.unpack('i',f.read(4))[0]==1
        logy=struct.unpack('i',f.read(4))[0]==1
        lutindex=struct.unpack('i',f.read(4))[0]
        #note that this binsize is not in units
        binSize=struct.unpack('i',f.read(4))[0]
        #templut=readintarray(f,256)
        #note this will be argbargb...
        templut=readubytearray(f,1024)
        npts=[]
        maxpts=struct.unpack('i',f.read(4))[0]
        npts.append(maxpts)
        xValues=readfltarray(f,maxpts)
        yValues=readfltarray(f,maxpts)
    finally:
        f.close()
    logxmin=math.log(findmingt0(xValues,xMax))
    logymin=math.log(findmingt0(yValues,yMax))
    histbins=get2DHistBins(binSize,xMin,xMax,yMin,yMax,logx,logy,logxmin,logymin)
    #now transform the lut to a matplotlib listedcolormap
    tcolors=[]
    for i in range(0,256):
        r=float(templut[i*4+2])/256.0
        g=float(templut[i*4+1])/256.0
        b=float(templut[i*4+0])/256.0
        tcolors.append([r,g,b])
    return xValues,yValues,histbins,xLabel,yLabel,[xMin,xMax,yMin,yMax,intMin,intMax],[logx,logy],col.ListedColormap(tcolors)

def get2DHistBins(binSize,xMin,xMax,yMin,yMax,logx,logy,logxmin=1.0,logymin=1.0):
    #need to generate the histogram bins
    histSize=256
    newhistsize=int(histSize/binSize)
    #not sure if this is the right kind of 2D array
    histbins=[]
    tempxbins=[]
    tempybins=[]
    if not logx and not logy:
        tbinsizex=(binSize/float(histSize))*(xMax-xMin)
        tbinsizey=(binSize/float(histSize))*(yMax-yMin)
        for i in range(0,newhistsize):
            tempxbins.append(xMin+tbinsizex*float(i))
        for i in range(0,newhistsize):
            tempybins.append(yMin+tbinsizey*float(i))
    else:
        #find the x bin edges
        if logx:
            if xMin>0.0:
                logxmin=math.log(xMin)
            #else: 
            #    xMin=findmingt0(xValues,xMax)
            #    logxmin=math.log(xMin)
            logxmax=math.log(xMax)
            tbinsizex=(binSize/float(histSize))*(logxmax-logxmin)
            for i in range(0,newhistsize):
                val=math.exp(logxmin+tbinsizex*float(i))
                tempxbins.append(val)
        else:
            tbinsizex=(binSize/float(histSize))*(xMax-xMin)
            for i in range(0,newhistsize):
                tempxbins.append(xMin+tbinsizex*float(i))
        #find the y bin edges
        if logy:
            if yMin>0.0:
                logymin=math.log(yMin)
            #else: 
            #    yMin=findmingt0(yValues,yMax)
            #    logymin=math.log(yMin)
            logymax=math.log(yMax)
            tbinsizey=(binSize/float(histSize))*(logymax-logymin)
            for i in range(0,newhistsize):
                val=math.exp(logymin+tbinsizey*float(i))
                tempybins.append(val)
        else:
            tbinsizey=(binSize/float(histSize))*(yMax-yMin)
            for i in range(0,newhistsize):
                tempybins.append(yMin+tbinsizey*float(i))
    #combine them
    histbins.append(tempxbins)
    histbins.append(tempybins)
    return histbins
    
def traj3DRead(path):
    #here we read a traj3D (id=2)
    f=open(path,"rb")
    try:
        xLabel=readstring(f)
        if xLabel=="pw2_file_type":
            id=struct.unpack('i',f.read(4))[0]
            xLabel=readstring(f)
        else:
            id=2
        if id!=2:
            return None
        yLabel=readstring(f)
        zLabel=readstring(f)
        #print("xlab="+xLabel)
        #print("id="+str(id))
        nseries=struct.unpack('i',f.read(4))[0]
        maxxpts=struct.unpack('i',f.read(4))[0]
        maxypts=0
        xMin=struct.unpack('f',f.read(4))[0]
        xMax=struct.unpack('f',f.read(4))[0]
        yMin=struct.unpack('f',f.read(4))[0]
        yMax=struct.unpack('f',f.read(4))[0]
        zMin=struct.unpack('f',f.read(4))[0]
        zMax=struct.unpack('f',f.read(4))[0]
        logx=struct.unpack('i',f.read(4))[0]==1
        logy=struct.unpack('i',f.read(4))[0]==1
        logz=struct.unpack('i',f.read(4))[0]==1
        npts=[]
        xValues=[]
        yValues=[]
        zValues=[]
        shapes=[]
        colors=[]
        for i in range(0,nseries):
            npts.append(struct.unpack('i',f.read(4))[0])
            shapes.append(struct.unpack('i',f.read(4))[0])
            colors.append(struct.unpack('i',f.read(4))[0])
            #print("npts"+`i`+"="+`npts[i]`)
            xValues.append(readfltarray(f,npts[i]))
            yValues.append(readfltarray(f,npts[i]))
            zValues.append(readfltarray(f,npts[i]))
            
    finally:
        f.close()
    return xValues,yValues,zValues,xLabel,yLabel,zLabel,[xMin,xMax,yMin,yMax,zMin,zMax],[logx,logy,logz],colors,shapes

def findmingt0(arr,maxval):
    minval=maxval
    for i in range(0,len(arr)):
        if arr[i]>0.0 and arr[i]<minval:
            minval=arr[i]
    return minval

def readstring(f):
    #first read an int giving the string length
    temp=struct.unpack('i',f.read(4))[0]
    #print("strlen="+`temp`)
    #and now the string itself
    barr=readbytearray(f,temp)
    return str(barr.tobytes(),'utf-8')
    #return barr.decode("utf-8")

def readfltarray(f,len):
    a=array.array('f')
    a.fromfile(f,len)
    return a
    
def readintarray(f,len):
    a=array.array('i')
    a.fromfile(f,len)
    return a

def readbytearray(f,len):
    a=array.array('b')
    a.fromfile(f,len)
    return a

def readubytearray(f,len):
    a=array.array('B')
    a.fromfile(f,len)
    return a
    
def getcolor(colnum):
    carr=['k','b','g','r','m','c','y','orange']
    return carr[colnum]

def getshape(shapenum):
    sarr=['-','s','+','x','^','|']
    return sarr[shapenum]
    
def getlimits(xVals,yVals):
    limits=[min(xVals[0]),max(xVals[0]),min(yVals[0]),max(yVals[0])]
    for i in range(1,len(yVals)):
        tempymin=min(yVals[i])
        tempymax=max(yVals[i])
        if(limits[2]>tempymin): limits[2]=tempymin
        if(limits[3]<tempymax): limits[3]=tempymax
    for i in range(1,len(xVals)):
        tempxmin=min(xVals[i])
        tempxmax=max(xVals[i])
        if(limits[0]>tempxmin): limits[0]=tempxmin
        if(limits[1]<tempxmax): limits[1]=tempxmax
    return limits
    
def getcolors(nser):
    colors=[]
    for i in range(0,nser):
        colors.append(i%8)
    return colors;
     
def getshapes(nser):
    shapes=[]
    for i in range(0,nser):
        shapes.append(i%6)
    return shapes;
    
def getxvals(yVals,xVals1):
    #here we get default x values
    #if xVals1 is blank, make them up
    xValues=[]
    if not xVals1:
        for i in range(0,len(yVals)):
            xValues.append=range(0,len(yVals[i]))
    else:
        #if xVals1 is not blank, append it repeatedly to the list
        if len(xVals1)==1:
            xValues.append(xVals1[0][0:len(yVals[i])])
        else:
            xValues.append(xVals1[0:len(yVals[i])])
    return xValues

def drawplot4(xVals,yVals,xLab,yLab,limits,logs,colors,shapes,errs):
    if(xVals.length<yVals.length):
        xVals=getxvals(yVals,xVals)
    if not limits:
        limits=getlimits(xVals,yVals)
    if not logs:
        logs=[False,False]
    if not colors:
        colors=getcolors(len(yVals))
    if not shapes:
        shapes=getshapes(len(yVals))
    for i in range(0,len(yVals)):
        if not errs:
            #print(getcolor(colors[i])+getshape(shapes[i]))
            if (shapes[i]==0): plt.plot(xVals[i],yVals[i],color=getcolor(colors[i]),linestyle=getshape(shapes[i]))
            else: plt.plot(xVals[i],yVals[i],color=getcolor(colors[i]),marker=getshape(shapes[i]))
        else:
            #assume lower errors are same as upper
            plt.errorbar(xVals[i],yVals[i],errs[2*i],fmt=getshape(shapes[i])+getcolor(colors[i]))
    plt.xlabel(xLab)
    plt.ylabel(yLab)
    plt.axis(limits)
    if logs[0]: plt.xscale('log')
    if logs[1]: plt.yscale('log')
    plt.show()
    
def drawplothist(xVals,histbins,xLab,yLab,limits,logs,color):
    plt.hist(xVals,histbins,facecolor=getcolor(color))
    plt.xlabel(xLab)
    plt.ylabel(yLab)
    plt.axis(limits)
    if logs[0]: plt.xscale('log')
    if logs[1]: plt.yscale('log')
    plt.show()
    
def drawplot2Dhist(xVals,yVals,histbins,xLab,yLab,limits,logs,colormap):
    #plt.hist2d(xVals,yVals,histbins,cmin=limits[4],cmax=limits[5],cmap=colormap)
    #plt.hist2d(xVals,yVals,histbins,cmin=limits[4],cmax=limits[5])
    counts, _, _=npy.histogram2d(xVals,yVals,histbins)
    fig, ax =plt.subplots()
    if(len(limits)<5):
        minint=0.0
        maxint=npy.max(counts)
    else:
        minint=limits[4]
        maxint=limits[5]
    ax.pcolormesh(histbins[0],histbins[1],counts.T,cmap=colormap,vmin=minint,vmax=maxint)
    plt.xlabel(xLab)
    plt.ylabel(yLab)
    ax.axis([limits[0],limits[1],limits[2],limits[3]])
    if logs[0]: ax.set_xscale('log')
    if logs[1]: ax.set_yscale('log')
    plt.show()
    
def drawcolormap(colormap,minval,maxval,cmlabel):
    fig=plt.figure(figsize=(8,1))
    ax1=fig.add_axes([0.05,0.8,0.9,0.15])
    cb1=mpl.colorbar.ColorbarBase(ax1,cmap=colormap,norm=col.Normalize(vmin=minval,vmax=maxval),orientation='horizontal')
    cb1.set_label(cmlabel)
    plt.show()
    
def getNiceColormap(whiteback):
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
    tcolors=[]
    for i in range(256):
        tcolors.append([r[i]/256.0,g[i]/256.0,b[i]/256.0])
    return col.ListedColormap(tcolors)
    
def drawplots(fname):
    print("file name = "+fname)
    ftype=gettype(fname)
    if ftype==0:
        xVals,yVals,xLab,yLab,limits,logs,colors,shapes,errs,annot=plot4read(fname)
        drawplot4(xVals,yVals,xLab,yLab,limits,logs,colors,shapes,errs)
        return xVals,yVals,xLab,yLab,limits,logs,colors,shapes,errs,annot
    if ftype==3:
        #plot the histogram
        xVals,histbins,xLab,yLab,limits,logs,color=plothistread(fname)
        drawplothist(xVals,histbins,xLab,yLab,limits,logs,color)
        return xVals,histbins,xLab,yLab,limits,logs,color
    if ftype==4:
        #plot the 2d histogram
        xVals,yVals,histbins,xLab,yLab,limits,logs,colormap=plot2Dhistread(fname)
        drawplot2Dhist(xVals,yVals,histbins,xLab,yLab,limits,logs,colormap)
        drawcolormap(colormap,limits[4],limits[5],'Density')
        return xVals,yVals,histbins,xLab,yLab,limits,logs,colormap
    
if __name__ == "__main__":
    #Tk().withdraw()
    #fname=askopenfilename()
    fname='C:/Users/jru/Desktop/test_plot_windows_python/gaus_func.pw2'
    #fname='C:/Users/jru/Desktop/test_plot_windows_python/17cy163_A07_Ngr1_3f_hist.pw2'
    #fname='c:/Users/jru/Desktop/gerton_screen/plate3_traj_norm_sub.pw2'
    #fname='c:/Users/jru/Desktop/conaway_proseq_chip_compare/pem2_1_wt1_combined_bestfit_addproseq.pw2'
    #root = Tk()
    #root.filename=askopenfilename();
    #fname=root.filename
    #this makes plots interactive
    #%matplotlib qt
    retvals=drawplots(fname)