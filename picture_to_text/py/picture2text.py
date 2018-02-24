
#coding=utf-8

import sys, getopt
import math
from PIL import Image

module_name = "picture2text"

def usage():
    print "[usage]:\t"+module_name + '.py -i <inputfile> -o <outputfile> -s <scale>'
    print '\t\t-i specify input image file'
    print '\t\t-o specify output xlsx file'
    print '\t\t-s specify picture scale'
    print '\t\t-s specify picture scale'

## Calculate the NTSC luminance value of an rgb triple
def luminance(color):
    return color[0]*0.30 + color[1]*0.59 + color[2]*0.11

## Calculate the CIE luminance value of an rgb triple
def luminanceCIE(color):
    return color[0]*0.30 + color[1]*0.59 + color[2]*0.11


def averagechannel(color):
    return (color[0] + color[1] + color[2]) / 3.0


g_lumchar = [ 'M', 'N', 'H', 'Q', '$', 'O', 'C', '?', '7', '>', '!', ':','-', ';', '.', ' ' ]

def ConvertToFloat(uchar):
    return uchar / 256.0

def picture_to_text(inputfile, outputfile, scale):
    if inputfile == None:
        return
    if outputfile == None:
        outputfile = inputfile + ".txt"

    im = Image.open(inputfile)
    print("old state:", im.format, im.size, im.mode)
    im.thumbnail((im.size[0]//scale, im.size[1]//scale))
    width = im.size[0]
    height = im.size[1]
    print("new state:", im.format, im.size, im.mode)
    pix = im.load()

    str = ""
    for y in range(height):
        for x in range(width):
            ls = pix[x, y]
            if len(ls) < 3:
                continue
            ls = map(ConvertToFloat, ls)
            lum = averagechannel(ls)
            str = str + g_lumchar[int(math.floor(lum*len(g_lumchar)))]
        str = str + "\n"
    
    with open(outputfile, 'w') as f:
        f.write(str)

    
def main(argv):
    inputfile = None
    outputfile = None
    scale = 1
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:r:c:",["ifile=","ofile=","scale="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-s", "--scale"):
            scale = int(arg)
    if inputfile == None:
        return usage()
    print 'input file:', inputfile
    print 'output file:', outputfile
    print 'scale:', scale
    picture_to_text(inputfile, outputfile, scale)
    
if __name__ == '__main__':
    main(sys.argv[1:])

