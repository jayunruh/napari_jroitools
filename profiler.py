# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 20:33:41 2020

@author: jru
"""
import numpy as np
from numba import jit

#these are convenience functions for the profile creation
@jit(nopython=True)
def getParallelCoords(coords,distance):
    if(distance==0.0):
        return coords
    #first get the parallel coordinates
    if coords[2]==coords[0]:
        xinc,yinc=1.0,0.0
    elif coords[3]==coords[1]:
        xinc,yinc=0.0,1.0
    else:
        slope=(coords[3]-coords[1])/(coords[2]-coords[0])
        #perpendicular slope
        newslope=-1.0/slope
        xinc=np.sqrt(1.0/(1.0+newslope*newslope))
        yinc=newslope*xinc

    newcoords=np.array([xinc,yinc,xinc,yinc])
    newcoords*=distance
    newcoords+=coords
    return newcoords

@jit(nopython=True)
def getLineLength(coords):
    len1=np.sqrt((coords[2]-coords[0])**2+(coords[3]-coords[1])**2)
    return int(len1+1)

@jit(nopython=True)
def interp2d(img,x,y):
    #simple bilinear interpolation for an array of x and y values
    prevx=np.floor(x).astype(np.int32)
    remx=x-prevx
    remx[prevx<0]=0.0
    prevx[prevx<0]=0
    remx[prevx>=img.shape[1]]=1.0
    prevx[prevx>=img.shape[1]]=img.shape[1]-1
    nextx=prevx+1
    prevy=np.floor(y).astype(np.int32)
    remy=y-prevy
    remy[prevy<0]=0.0
    prevy[prevy<0]=0
    remy[prevy>=img.shape[0]]=1.0
    prevy[prevy>=img.shape[0]]=img.shape[0]-1
    nexty=prevy+1
    #x1=img[prevy,prevx]*(1.0-remx)+remx*img[prevy,nextx]
    #x2=img[nexty,prevx]*(1.0-remx)+remx*img[nexty,nextx]
    #have to do some gymnastics here because of numba restrictions
    ul=np.array([img[prevy[i],prevx[i]] for i in range(len(prevy))])
    ur=np.array([img[prevy[i],nextx[i]] for i in range(len(prevy))])
    ll=np.array([img[nexty[i],prevx[i]] for i in range(len(nexty))])
    lr=np.array([img[nexty[i],nextx[i]] for i in range(len(nexty))])
    x1=ul*(1.0-remx)+remx*ur
    x2=ll*(1.0-remx)+remx*lr
    return x1*(1.0-remy)+remy*x2

@jit(nopython=True)
def interpLine(coords,linelength,img):
    xpts=np.linspace(coords[0],coords[2],linelength)
    ypts=np.linspace(coords[1],coords[3],linelength)
    return interp2d(img,xpts,ypts)

#now we need to interpolate repeatedly over parallel lines to get the profile
#assume line is in single z plane
#line coordinates are two sets of z,y,x
@jit(nopython=True)
def getThickLineProfile(img,linecoords,thickness):
    #change coords to x1,y1,x2,y2
    coords=np.array([linecoords[0][2],linecoords[0][1],linecoords[1][2],linecoords[1][1]])
    print(coords)
    halfthick=thickness/2.0
    #get the imge plane of interest
    zcoord=int(linecoords[0][0])
    print(zcoord)
    img2d=img[zcoord,:,:]
    linelength=getLineLength(coords)
    avgline=interpLine(getParallelCoords(coords,-halfthick),linelength,img2d)
    for i in range(1,int(thickness)):
        tempcoords=getParallelCoords(coords,-halfthick+i)
        templine=interpLine(tempcoords,linelength,img2d)
        avgline+=templine
    avgline/=thickness
    return avgline

#this version strings together several thick line profiles into a longer polyline profile
#need to eliminate the end points for each segment (except the last) to avoid duplication
@jit(nopython=True)
def getThickPolylineProfile(img,linecoords,thickness):
    npts=len(linecoords)
    profiles=[]
    for i in range(1,npts):
        yvals=getThickLineProfile(img,linecoords[i-1:i+1],thickness)
        if i==(npts-1):
            profiles.append(yvals)
        else:
            profiles.append(yvals[:-2])
    return np.concatenate(profiles)

#this version takes an nbeads x ngenes spatial transcriptomics matrix and makes a polyline profile
@jit(nopython=True)
def getThickBeadProfile(gematrix,beadpos,linecoords,thickness):
    npts=len(linecoords)
    profiles=[]
    for i in range(1,npts):
        profile=getThickBeadLineProfile(gematrix,beadpos,linecoords[i-1:i+1],thickness)
        if i==(npts-1):
            profiles.append(profile)
        else:
            profiles.append(profile[:-2,:])
    return np.concatenate(profiles,axis=0)

#this version takes an nbeads x ngenes spatial transcriptomics matrix and makes a line profile
#output is distance x ngenes
#@jit(nopython=True)
def getThickBeadLineProfile(gematrix,beadpos,linecoords,thickness):
    coords=np.array([linecoords[0][2],linecoords[0][1],linecoords[1][2],linecoords[1][1]])
    print(coords)
    halfthick=thickness/2.0
    ucoords=getParallelCoords(coords,halfthick)
    lcoords=getParallelCoords(coords,-halfthick)
    #need to figure out which beads are in this profile
    rectcoords=np.array([ucoords[0:2],ucoords[2:4],lcoords[2:4],lcoords[0:2]])
    contained=np.apply_along_axis(lambda x:rectContains(rectcoords,x),axis=1,arr=beadpos)
    valid=np.where(contained)[0]
    #linelength=getLineLength(coords)
    flinelength=np.sqrt((coords[2]-coords[0])**2+(coords[3]-coords[1])**2)
    linelength=int(flinelength)
    #get the array of distances between bead coordinates and the first line point
    #this is the dot product with the line
    dists=((coords[2]-coords[0])*(beadpos[valid,0]-coords[0])+(coords[3]-coords[1])*(beadpos[valid,1]-coords[1]))/flinelength
    dists=np.floor(dists).astype(int)
    #do a clip just to make sure we don't have any at the very end of the line
    dists=dists.clip(0,linelength-1)
    #now add up the gematrix columns for each unit bin
    geprofile=np.zeros((linelength,gematrix.shape[0]),dtype=float)
    #will this work?
    geprofile[dists,:]+=gematrix[:,valid].T
    return geprofile

#find out if a point is in a triangle
#point is an x,y list
#triangle is an [x1,y1],[x2,y2],[x3,y3] list
#calculate the z cross product component for 3 potential subtriangles
#all should be same sign
@jit(nopython=True)
def triangleContains(triangle,point):
    #third component of the cross product
    cp3 = lambda p1,p2,p3 : (p1[0]-p3[0])*(p2[1]-p3[1])-(p2[0]-p3[0])*(p1[1]-p3[1])
    temp=np.array([cp3(point,triangle[0],triangle[1]),
    cp3(point,triangle[1],triangle[2]),
    cp3(point,triangle[2],triangle[0])])
    return (temp>=0.0).all() or (temp<0.0).all()

#find out if a 4 point convex polygon contains a point
#split into two triangles and test each
#rectangle points should be in order
@jit(nopython=True)
def rectContains(rect,point):
    return triangleContains([rect[0],rect[1],rect[2]],point) or triangleContains([rect[2],rect[3],rect[0]],point)
    
#copy of the contains code from ImageJ FloatPolygon: https://imagej.nih.gov/ij/developer/source/ij/process/FloatPolygon.java.html
@jit(nopython=True)
def polyContains(polygon,point):
    inside=False
    y=point[1]
    x=point[0]
    for i in range(polygon.shape[0]):
        if(i>0): j=i-1
        else: j=polygon.shape[0]-1
        if(((polygon[i,0]>=y)!=(polygon[j,0]>=y)) and (x>(polygon[j,1]-polygon[i,1])*(y-polygon[i,0])/(polygon[j,0]-polygon[i,0])+polygon[i,1])):
            inside=(not inside)
    return inside