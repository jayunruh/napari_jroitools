# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 08:01:36 2021
License is GNU GPLv2
@author: Jay Unruh
"""

import numpy as np
import struct
import math
import array
import sys
import os

class RoiDecoder():

    def __init__(self):
        #offsets
        self.VERSION_OFFSET = 4
        self.TYPE = 6
        self.TOP,self.LEFT,self.BOTTOM,self.RIGHT = 8,10,12,14
        self.N_COORDINATES = 16
        self.X1,self.Y1,self.X2,self.Y2,self.XD,self.YD = 18,22,26,30,18,22
        self.WIDTHD = 26
        self.HEIGHTD = 30
        self.SIZE = 18
        self.STROKE_WIDTH = 34
        self.SHAPE_ROI_SIZE = 36
        self.STROKE_COLOR = 40
        self.FILL_COLOR = 44
        self.SUBTYPE = 48
        self.OPTIONS = 50
        self.ARROW_STYLE = 52
        self.FLOAT_PARAM = 52
        self.POINT_TYPE= 52
        self.ARROW_HEAD_SIZE = 53
        self.ROUNDED_RECT_ARC_SIZE =54
        self.POSITION = 56
        self.HEADER2_OFFSET = 60
        self.COORDINATES = 64
        #header2 offsets
        self.C_POSITION,self.Z_POSITION,self.T_POSITION = 4,8,12
        self.NAME_OFFSET = 16
        self.NAME_LENGTH = 20
        self.OVERLAY_LABEL_COLOR = 24
        self.OVERLAY_FONT_SIZE = 28
        self.GROUP = 30
        self.IMAGE_OPACITY = 31
        self.IMAGE_SIZE = 32
        self.FLOAT_STROKE_WIDTH = 36
        self.ROI_PROPS_OFFSET = 40
        self.ROI_PROPS_LENGTH = 44
        self.COUNTERS_OFFSET = 48
        #subtypes
        self.TEXT,self.ARROW,self.ELLIPSE,self.IMAGE,self.ROTATED_RECT=1,2,3,4,5
        #options
        self.SPLINE_FIT=1
        self.DOUBLE_HEADED=2
        self.OUTLINE=4
        self.OVERLAY_LABELS=8
        self.OVERLAY_NAMES=16
        self.OVERLAY_BACKGROUNDS=32
        self.OVERLAY_BOLD=64
        self.SUB_PIXEL_RESOLUTION=128
        self.DRAW_OFFSET=256
        self.ZERO_TRANSPARENT=512
        self.SHOW_LABELS=1024
        self.SCALE_LABELS=2048
        self.PROMPT_BEFORE_DELETING=4096
        self.SCALE_STROKE_WIDTH=8192
        #types
        self.polygon,self.rect,self.oval,self.line,self.freeline=0,1,2,3,4
        self.polyline,self.noRoi,self.freehand,self.traced,self.angle,self.point=5,6,7,8,9,10
    
    def readzip(self,path):
        #read a zip file of rois
        from zipfile import ZipFile
        rois=[]
        with ZipFile(path,'r') as zipobj:
            flist=zipobj.namelist()
            for fname in flist:
                print(fname)
                with zipobj.open(fname) as fp:
                    #barr=np.fromfile(fp,dtype='b',count=-1)
                    barr=fp.read()
                    barr=np.array(bytearray(barr))
                    rois.append(self.readroibytes(barr,fname))
        return rois

    def readroi(self,path):
        #start by reading the file into a byte array
        f=open(path,"rb")
        try:
            barr=np.fromfile(f,dtype='b',count=-1)
        finally:
            f.close()
        name=os.path.basename(path)
        return self.readroibytes(barr,name)

    def readroibytes(self,barr,name):
        size=len(barr)
        #name=os.path.basename(path)
        label=readstring(barr[0:4])
        #the first label should be "Iout"
        if label!="Iout":
            print("not a valid roi file")
            return
        version=readmotorolashort(barr,self.VERSION_OFFSET,1)[0]
        print('version:'+str(version))
        type1=barr[self.TYPE]
        print('type:'+str(type1))
        subtype=readmotorolashort(barr,self.SUBTYPE,1)[0]
        print('subtype:'+str(subtype))
        top,left,bottom,right=readmotorolashort(barr,self.TOP,4)
        print('bounds:')
        print([top,left,bottom,right])
        width=right-left
        height=bottom-top
        ncoords=readmotorolashort(barr,self.N_COORDINATES,1)[0]
        if ncoords==0:
            ncoords=readmotorolaint(barr,self.SIZE,1)[0]
        print('n coords:'+str(ncoords))
        options=readmotorolashort(barr,self.OPTIONS,1)[0]
        print('options:'+str(options))
        position=readmotorolaint(barr,self.POSITION,1)[0]
        print('position:'+str(position))
        hdr2Offset=readmotorolaint(barr,self.HEADER2_OFFSET,1)[0]
        print('header2 offset:'+str(hdr2Offset))
        channel,slice1,frame=0,0,0
        overlaylabelColor=0
        overlayFontSize=0
        group=0
        imageOpacity=0
        imageSize=0
        subPixelResolution=((options & self.SUB_PIXEL_RESOLUTION)!=0 and version>=222)
        drawOffset=(subPixelResolution and (options & self.DRAW_OFFSET)!=0)
        scaleStrokeWidth=True
        if (version>=228):
            scaleStrokeWidth=(options & self.SCALE_STROKE_WIDTH)!=0
        subPixelRect=(version>=223 and subPixelResolution and (type==self.rect or type==self.oval))
        xd,yd,widthd,heightd=0.0,0.0,0.0,0.0
        if (subPixelRect):
            xd,yd=readmotorolafloat(barr,self.XD,2)
            widthd,heightd=readmotorolafloat(barr,self.WIDTHD,2)
        if(hdr2Offset>0 and (hdr2Offset+self.IMAGE_SIZE+4)<=size):
            channel,slice1,frame=readmotorolaint(barr,hdr2Offset+self.C_POSITION,3)
            overlayLabelColor=readmotorolaint(barr,hdr2Offset+self.OVERLAY_LABEL_COLOR,1)[0]
            overlayFontSize=readmotorolashort(barr,hdr2Offset+self.OVERLAY_FONT_SIZE,1)[0]
            imageOpacity=barr[hdr2Offset+self.IMAGE_OPACITY]
            imageSize=readmotorolaint(barr,hdr2Offset+self.IMAGE_SIZE,1)[0]
            group=barr[hdr2Offset+self.GROUP]
        if(name!=None and name[-4:]==".roi"):
            name=name[0:-4]
        isComposite=readmotorolaint(barr,self.SHAPE_ROI_SIZE,1)[0]>0
        roi=None
        if(isComposite):
            #I'm not implementing these composite rois for now
            return None
        if(type1==self.rect):
            print('rect type')
            if(subPixelRect):
                xcoords,ycoords=self.makeRect(xd,yd,widthd,heightd)
                roi=Roi(xcoords,ycoords)
            else:
                xcoords,ycoords=self.makeRect(left,top,width,height)
                roi=Roi(xcoords,ycoords)
            #not implementing arc corners yet
            arcSize=readmotorolashort(barr,self.ROUNDED_RECT_ARC_SIZE,1)[0]
        elif(type1==self.oval):
            print('oval type')
            if(subPixelRect):
                xcoords,ycoords=self.makeRect(xd,yd,widthd,heightd)
                roi=Roi(xcoords,ycoords,rtype=self.oval)
            else:
                xcoords,ycoords=self.makeRect(left,top,width,height)
                roi=Roi(xcoords,ycoords,rtype=self.oval)
        elif(type1==self.line):
            print('line type')
            x1,y1,x2,y2=readmotorolafloat(barr,self.X1,4)
            roi=Roi([x1,x2],[y1,y2],rtype=self.line)
            #if(subtype==self.ARROW):
                #note that arrow is implemented as a line here for now
            
        #elif(type1==self.polygon or type1==self.freehand or type1==self.traced or type1==self.freeline or type1==self.angle or type1==self.point):
        else:
            if(ncoords<=0): return None
            x,y=None,None
            xf,yf=None,None
            base1=self.COORDINATES
            #base2=base1+2*ncoords
            xtmp,ytmp=None,None
            tmpdata=readmotorolashort(barr,base1,ncoords*2)
            tmpdata=np.clip(tmpdata,a_min=0,a_max=None)
            x=tmpdata[:ncoords]+left
            y=tmpdata[ncoords:]+top
            if(subPixelResolution):
                print('subPixelResolution is true')
                base1=self.COORDINATES+4*ncoords
                #base2=base1+4*n
                tmpdata=readmotorolafloat(barr,base1,ncoords*2)
                xf=tmpdata[:ncoords]
                yf=tmpdata[ncoords:]
            if(type1==self.point):
                print('point type')
                if(subPixelResolution):
                    roi=Roi([xf],[yf],rtype=self.point)
                else:
                    roi=Roi([x],[y],rtype=self.point)
                #if(version>=226):
                    #these are options I don't support for point size
                #break
            elif(type1==self.freehand):
                print('freehand type')
                if(subtype==self.ELLIPSE or subtype==ROTATED_RECT):
                    #these are special data types
                    #need to implement these but maybe later
                    None
                else:
                    if(subPixelResolution):
                        roi=Roi(xf,yf,rtype=self.freehand)
                    else:
                        roi=Roi(x,y,rtype=self.freehand)
            else:
                print('polygon type')
                #let's just make everything else a polygon
                if(subPixelResolution):
                    roi=Roi(xf,yf,rtype=self.polygon)
                else:
                    roi=Roi(x,y,rtype=self.polygon)
        if(roi==None):
            return None
        roi.name=self.getRoiName(barr,name)
        if(version>=218):
            #here we get the thickness and color info
            thickness,color,fcolor=self.getStrokeWidthAndColor(barr,roi,hdr2Offset)
            roi.thickness=thickness
            roi.color=color
        if(version>=218 and subtype==self.TEXT):
            #don't support this but read it anyway
            troiname,troitext=getTextRoi(roi,version)
        if(version>=221 and subtype==self.IMAGE):
            #don't support this and won't read it
            None
        if(version>=227):
            #don't support point counters and won't read them
            None
        if(version>=228 and group>0):
            #don't support group numbers for now
            None
        roi.position=position
        if(channel>0 or slice1>0 or frame>0):
            roi.position=[channel,slice1,frame]
        return roi
    
    def getTextRoi(self,barr,version):
        #don't support this version so this is just a placeholder
        #hdrSize=self.HEADER_SIZE
        hdrSize=64
        namelength=readmotorolaint(barr,hdrSize+8,1)[0]
        textlength=readmotorolaint(barr,hdrSize+12,1)[0]
        namevals=readmotorolashort(barr,hdSize+16,namelength)
        name=readstring(namevals)
        textvals=readmotorolashort(barr,hdSize+16+namelength*2,namelength)
        text=readstring(textvals.astype(np.byte))
        return name,text
    
    def getStrokeWidthAndColor(self,barr,roi,hdr2Offset):
        strokeWidth=readmotorolashort(barr,self.STROKE_WIDTH,1)[0]
        if(hdr2Offset>0):
            strokeWidthD=readmotorolafloat(barr,hdr2Offset+self.FLOAT_STROKE_WIDTH,1)[0]
            if(strokeWidthD>0.0): strokeWidth=strokeWidthD
        strokeColor=barr[self.STROKE_COLOR:self.STROKE_COLOR+4]
        fillColor=barr[self.FILL_COLOR:self.FILL_COLOR+4]
        return strokeWidth,strokeColor,fillColor
    
    def getRoiName(self,barr,fileName):
        hdr2Offset=readmotorolaint(barr,self.HEADER2_OFFSET,1)[0]
        if(hdr2Offset==0): return fileName
        offset=readmotorolaint(barr,hdr2Offset+self.NAME_OFFSET,1)[0]
        nlength=readmotorolaint(barr,hdr2Offset+self.NAME_LENGTH,1)[0]
        if(offset==0 or nlength==0):
            return fileName
        #for some reason the character values are stored in short values
        namevals=readmotorolashort(barr,offset,nlength)
        #convert to bytes and then to string
        return readstring(namevals.astype(np.byte))
    
    def makeRect(self,x,y,width,height):
        xcoords=[x,x+width,x+width,x]
        ycoords=[y,y,y+height,y+height]
        return xcoords,ycoords
    
    def getShapeRoi(self,barr):
        #this is attempting composite rois
        #those are encoded as a complex combination of drawing instructions
        #I'm not implementing this for now
        '''
        rtype=barr[self.TYPE]
        if(rtype!=self.rect):
            return None
        top,left,bottom,right=readmotorolashort(barr,self.TOP,4)
        width=right-left
        height=bottom-top
        n=readmotorolaint(barr,self.SHAPE_ROI_SIZE,1)[0]
        roi=None
        base=self.COORDINATES
        temp=readmotorolafloat(barr,self.COORDINATES,n)
        return None
        '''
        return None
    
class Roi():
    
    def __init__(self,xcoords,ycoords,closed=True,position=None,color=None,thickness=1,rtype=1,name=None):
        self.xcoords=xcoords
        self.ycoords=ycoords
        self.closed=closed
        #note that position will be a single value or a CZT array
        self.position=position
        self.color=color
        self.thickness=thickness
        self.rtype=rtype
        self.name=name
        #types
        self.types=['polygon','rect','oval','line','freeline','polyline','noRoi','freehand','traced','angle','point']
        
    def getType(self):
        return self.types[self.rtype]
        
    def getArray(self):
        #returns a numpy array of point pairs
        return np.array(list(zip(self.xcoords,self.ycoords)))
        
    def getNapariArray(self):
        #need to convert each roi to a numpy array of points
        #for some reason napari wants it in z,y,x order
        if(isinstance(self.position,list)):
            zcoords=[self.position[0]-1]*len(self.ycoords)
        else:
            zcoords=[self.position-1]*len(self.ycoords)
        return np.array(list(zip(zcoords,self.ycoords,self.xcoords)))
    
    def getBounds(self):
        x0=min(self.xcoords)
        y0=min(self.ycoords)
        width=max(self.xcoords)-x0
        height=max(self.ycoords)-y0
        return np.array([x0,y0,width,height])
    
    def getSubPixelResolution(self):
        residx=self.xcoords-np.floor(self.xcoords).astype(int)
        residy=self.ycoords-np.floor(self.ycoords).astype(int)
        rem=np.sum(residx**2)
        rem=rem+np.sum(residy**2)
        return rem>1.0e-6
        
    def getBounds(self):
        x=min(self.xcoords)
        y=min(self.ycoords)
        xmax=max(self.xcoords)
        ymax=max(self.ycoords)
        width=xmax-x
        height=ymax-y
        return [x,y,width,height]
        
    def getStandardName(self):
        r=self.getBounds()
        xc=int(r[0]+r[2]/2)
        yc=int(r[1]+r[3]/2)
        if(xc<0): xc=0
        if(yc<0): yc=0
        digits=4
        xs=str(xc)
        if(len(xs)>digits): digits=len(xs)
        ys=str(yc)
        if(len(ys)>digits): digits=len(ys)
        xs="000000"+xs
        ys="000000"+ys
        label=ys[-digits:]+'-'+xs[-digits:]
        if(self.position is not None):
            zc=0
            if(isinstance(self.position,list)):
                zc=self.position[0]
            else:
                zc=self.position
            zc=int(zc)
            zs="000000"+str(zc)
            label=zs[-digits:]+'-'+label
        return label+'.roi'
    
def readstring(barr):
    return str(barr.tobytes(),'utf-8')

def readintelfloat(barr,off,tlen):
    end=off+tlen*4
    return np.frombuffer(barr[off:end], dtype='<f',count=tlen)

def readmotorolafloat(barr,off,tlen):
    end=off+tlen*4
    return np.frombuffer(barr[off:end], dtype='>f',count=tlen)

def readintelshort(barr,off,tlen):
    end=off+tlen*2
    return np.frombuffer(barr[off:end], dtype='<h',count=tlen)

def readmotorolashort(barr,off,tlen):
    end=off+tlen*2
    return np.frombuffer(barr[off:end], dtype='>h',count=tlen)

def readintelint(barr,off,tlen):
    end=off+tlen*4
    return np.frombuffer(barr[off:end], dtype='<i',count=tlen)

def readmotorolaint(barr,off,tlen):
    end=off+tlen*4
    return np.frombuffer(barr[off:end], dtype='>i',count=tlen)