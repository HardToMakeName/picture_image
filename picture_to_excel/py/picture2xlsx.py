
#coding=utf-8

import sys, getopt
import xlsxwriter
from PIL import Image

module_name = "picture2xlsx"

def usage():
    print "[usage]:\t"+module_name + '.py -i <inputfile> -o <outputfile> -s <scale> -r <row_height> -w <col_width>'
    print '\t\t-i specify input image file'
    print '\t\t-o specify output xlsx file'
    print '\t\t-s specify picture scale'
    print '\t\t-r specify xlsx picture row height'
    print '\t\t-c specify xlsx picture col width'

def GetHexString(value):
    str = hex(value)
    str = str[2:]
    if len(str) == 1:
        str = "0" + str
    return str

    
def picture_to_xslx(inputfile, outputfile, scale, row_height = 5, col_width = 1):
    if inputfile == None:
        return
    if outputfile == None:
        outputfile = inputfile + ".xlsx"   


    im = Image.open(inputfile)
    print("old state:", im.format, im.size, im.mode)
    im.thumbnail((im.size[0]//scale, im.size[1]//scale))
    width = im.size[0]
    height = im.size[1]
    print("new state:", im.format, im.size, im.mode)
    pix = im.load()
    
    workbook = xlsxwriter.Workbook(outputfile)
    worksheet = workbook.add_worksheet()
    
    dic = {}
    worksheet.set_column(0, width, width=col_width)
    for x in range(width):
        worksheet.set_row(x, row_height)
        for y in range(height):
            ls = pix[x, y]
            if len(ls) < 3:
                continue
            r = ls[0]
            g = ls[1]
            b = ls[2]
            rgba="#" + GetHexString(r) + GetHexString(g) + GetHexString(b)
            format = None
            if dic.has_key(rgba):
                format = dic[rgba]
            else:
                format = workbook.add_format()
                format.set_bg_color(rgba)        
            worksheet.write(y, x, "  ", format) ##worksheet.write(y, x, "", format)  
    workbook.close()

    
def main(argv):
    inputfile = None
    outputfile = None
    scale = 1
    row_height = 5
    col_width = 1
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
        elif opt in ("-r", ):
            row_height = int(arg)
        elif opt in ("-w", ):
            col_width = int(arg)
    if inputfile == None:
        return usage()
    print 'input file:', inputfile
    print 'output file:', outputfile
    print 'scale:', scale
    print 'row_height:', row_height
    print 'col_width:', col_width
    picture_to_xslx(inputfile, outputfile, scale, row_height, col_width)
    
if __name__ == '__main__':
    main(sys.argv[1:])

