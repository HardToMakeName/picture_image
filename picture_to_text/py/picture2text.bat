python picture2text.py -i %1 -s 3
python txt2pdf.py --margin-left=1 --margin-right=0 --margin-top=0 --margin-bottom=0 --font-size=5 --media=A4 -o "%1.pdf" "%1.txt" 
::-q