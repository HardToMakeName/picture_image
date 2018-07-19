# coding=utf-8

import numpy
import os
import sys
import math
import os
import sys
import json
from PIL import Image


RIGHT = 0
LEFT = 1
FRONT = 2
BACK = 3
TOP = 4
DOWN = 5

## right, left, front, back, top, down
# globals NAME
NAME = ["right", "left", "front", "back", "top", "down"]




## GetXXXUV: 上下前后左右，人站在原点向6个方向看，与相应的面的投影UV
## UV相对于对应面的左上角

## +X 右
## -X 左
## +Y 前
## -Y 后
## +Z 上
## -Z 下

## 平躺在地上，右方向是+X
def GetTopUV(theta, phi):
    x = math.tan(theta)*math.cos(phi)
    y = math.tan(theta)*math.sin(phi)
    u = (1+x)/2
    v = (1+y)/2
    return u, v

## 趴在地上，右方向是+X
def GetBottonUV(theta, phi):
    x = -math.tan(theta)*math.cos(phi)
    y = -math.tan(theta)*math.sin(phi)
    u = (1+x)/2
    v = (1-y)/2
    return u, v

def GetRightUV(theta, phi):
    x = 1.0
    y = x*math.tan(phi)
    z = x/math.cos(phi)/math.tan(theta)
    u = (1-y)/2
    v = (1-z)/2
    return u, v

def GetLeftUV(theta, phi):
    x = -1.0
    y = x*math.tan(phi)
    z = x/math.cos(phi)/math.tan(theta)
    u = (y+1)/2
    v = (1-z)/2
    return u, v

def GetFrontUV(theta, phi):
    y = 1.0
    x = y / math.tan(phi)
    z = y / math.sin(phi) / math.tan(theta)
    u = (x+1)/2
    v = (1-z)/2
    return u, v

def GetBackUV(theta, phi):
    y = -1.0
    x = y / math.tan(phi)
    z = y / math.sin(phi) / math.tan(theta)
    u = (1-x)/2
    v = (1-z)/2

    # x = math.sin(theta) * math.cos(phi)
    # y = math.sin(theta) * math.sin(phi)
    # z = math.cos(theta)

    return u, v


## 返回相对图片左上角的UV坐标
def GetUVAndIndex(theta, phi):
    ##phi [-math.pi/4, math.pi*7/4)
    while phi > (math.pi*7/4):
        phi = phi - math.pi*2

    index = 0
    crisis = 0.0
    dispatchUV = GetRightUV
    if phi >= -math.pi/4 and phi < math.pi/4:
        x = 1
        zmax = 1
        crisis = math.atan2(x/math.cos(phi), zmax)
        index = RIGHT
        dispatchUV = GetRightUV

    elif phi >= math.pi/4 and phi < math.pi*3/4:
        y = 1
        zmax = 1
        crisis = math.atan2(y/math.sin(phi), zmax)
        index = FRONT
        dispatchUV = GetFrontUV

    elif phi >= math.pi*3/4 and phi < math.pi*5/4:
        x = -1
        zmax = 1
        crisis = math.atan2(x/math.cos(phi), zmax)
        index = LEFT
        dispatchUV = GetLeftUV

    elif phi >= math.pi*5/4 and phi < math.pi*7/4:
        y = -1
        zmax = 1
        crisis = math.atan2(y/math.sin(phi), zmax)
        index = BACK
        dispatchUV = GetBackUV


    if theta < crisis:
        index = TOP
        dispatchUV = GetTopUV
    elif theta > (math.pi - crisis):
        index = BOTTOM
        dispatchUV = GetBottonUV

    u, v = dispatchUV(theta, phi)

    ## 翻转U坐标
    u = 1.0 - u
    return index, (u, v)


def get_int_coord(x, min, max):
    # mm_clip = lambda x, l, u: max(l, min(u, x))
    # s_clip = lambda x, l, u: sorted((x, l, u))[1]
    py_clip = lambda x, l, u: l if x < l else u if x > u else x
    x = int(x)
    return py_clip(x, min, max)


def GetRGB(im, pix, u, v):
    width = im.size[0]
    height = im.size[1]
    x = (width-1) * u
    y = (height-1) * v

    x0 = math.floor(x)
    x1 = math.ceil(x)
    y0 = math.floor(y)
    y1 = math.ceil(y)

    tu, tv = 0., 0.
    if x1 != x0:
        tu = (x - x0)/(x1 - x0)
    if y1 != y0:
        tv = (y - y0)/(y1 - y0)


    x0 = get_int_coord(x0, 0, width-1 )
    x1 = get_int_coord(x1, 0, width-1)
    y0 = get_int_coord(y0, 0, height-1)
    y1 = get_int_coord(y1, 0, height-1)

    # 先在v方向插值，然后在u方向差值
    c00 = numpy.array(pix[x0, y0])
    c01 = numpy.array(pix[x1, y0])

    c0 = c00*(1.0-tv) + c01*tv

    c10 = numpy.array(pix[x1, y0])
    c11 = numpy.array(pix[x1, y1])

    c1 = c10*(1.0-tv) + c11*tv

    c = c0*(1.0-tu) + c1*tu

    R = 0
    G = 0
    B = 0
    if len(c.shape) == 0:
        return R, G, B
    if c.shape[0] >0:
        R = int(c[0])
    if c.shape[0]>1:
        G = int(c[1])
    if c.shape[0] >2:
        B = int(c[2])

    return R, G, B


def GetFullViewFromImages(dic, width, height):
    targetName = 'D:/target.png'
    if "output" in dic:
        targetName = dic["output"]


    imgTarget = Image.new('RGB', (width, height), (255,255,255))
    pixTarget = imgTarget.load()
    imgLs = [None, None, None, None, None, None]
    pixLs = [None, None, None, None, None, None]
    for i in range(0, len(NAME)):
        name = NAME[i]
        if name in dic:
            if os.path.isfile(dic[name]):
                im = Image.open(dic[name])
                if not im == None:
                    imgLs[i] = im
                    pixLs[i] = im.load()
                else:
                    print(dic[name], "cannot open the image.")

    for i in range(0, width):
        for j in range(0, height):
            # - math.pi / 4
            phi = 1.0*i/(width-1) * math.pi*2 + math.pi*3/2 ## 从-Y开始
            theta = 1.0*j/(height-1) * math.pi
            index, uv = GetUVAndIndex(theta, phi)
            u = uv[0]
            v = uv[1]
            r, g, b = 0, 0, 0
            if not imgLs[index]==None and not pixLs[index]==None:
                im = imgLs[index]
                pix = pixLs[index]
                r, g, b = GetRGB(im, pix, u, v)
                imgTarget.putpixel([i, j], (r, g, b))
    imgTarget.save(targetName)


def parseJson(jsonFileName):
    output = open(jsonFileName, 'r')
    output.seek(0, 2)
    size = output.tell()
    output.seek(0, 0)
    jsonData = output.read(size)
    dic = json.loads(jsonData)
    # print dic
    return dic



if __name__ == "__main__":
    if len(sys.argv) > 1:
        dic = {}
        dic = parseJson(sys.argv[1])

        width = 64
        height = 32

        if "width" in dic:
            width = dic["width"]
        if "height" in dic:
            height = dic["height"]

        GetFullViewFromImages(dic, width, height)

    ## print (GetTopUV(0,0))
    ## print (__name__)




# https://segmentfault.com/q/1010000007665266?_ea=1582761

# https://stackoverflow.com/questions/4092528/how-to-clamp-an-integer-to-some-range-in-python

# https://blog.csdn.net/cxmscb/article/details/54583415   python之numpy的基本使用