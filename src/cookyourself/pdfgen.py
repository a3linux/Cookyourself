import random
import string
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

P_YMARGIN = 60
P_XOFFSET = 55
L_XOFFSET = 50

H_LINEWIDTH = .5
P_LINEWIDTH = .3
H_FONTSIZE = 16
P_FONTSIZE = 12

PADDING = 10
P_LINESPACE = 20
FONTTYPE = 'Helvetica'
P_TAB1 = 30
P_TAB2 = 460

WIDTH, HEIGHT = pagesizes.letter

def print_shoppinglist_header(canvas):
    line = HEIGHT - P_YMARGIN
    canvas.setLineWidth(H_LINEWIDTH)
    canvas.setFont(FONTTYPE, H_FONTSIZE)
    canvas.drawString(P_XOFFSET, line, "Thanks for choosing Cookyourself!")
    canvas.setLineWidth(P_LINEWIDTH)
    canvas.setFont(FONTTYPE, P_FONTSIZE)
    line -= PADDING
    canvas.line(L_XOFFSET, line, WIDTH-L_XOFFSET,line)

def gen_shoplist_pdf(filename, products):
    c = canvas.Canvas(filename, pagesize=pagesizes.letter)

    count = 0
    total = 0
    line = HEIGHT - P_YMARGIN

    for product in products:
        if line < P_YMARGIN:
            c.showPage()
            line = HEIGHT - P_YMARGIN

        if line == HEIGHT - P_YMARGIN:
            print_shoppinglist_header(c)
            line -= (PADDING + P_LINESPACE)

        count += 1
        c.drawString(P_XOFFSET, line, '{:d}.'.format(count))
        c.drawString(P_XOFFSET+P_TAB1, line, product[0])
        c.drawString(P_XOFFSET+P_TAB2, line, '${:.1f}'.format(product[1]))
        line -= P_LINESPACE
        total += product[1]

    if line < P_YMARGIN:
        c.showPage()
        print_shoppinglist_header(c)

    c.drawString(P_XOFFSET, line, 'TOTAL:')
    c.drawString(P_XOFFSET+P_TAB2, line, '${:.1f}'.format(total))
    c.showPage()
    c.save()


if __name__ == '__main__':
    filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
    products = [('name', 10) for i in range(100)]
    gen_shoplist_pdf('helloworld.pdf', products)
