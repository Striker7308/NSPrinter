from doctest import debug

from font import print_bold_text
height_line = 8

def fill_cell(pdf, key, value, wk, wv, align='C', border=1, font_k='宋体', font_size=15, font_v='hetang', print_no_key=False):
    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_font(font_k, size=10)

    if print_no_key: wk = ''
    pdf.cell(wk, height_line, key, border=border, align=align)

    pdf.set_xy(pdf.get_x(), y)
    pdf.set_font(font_v, size=font_size)
    pdf.cell(wv, height_line, value, border=border)
    pdf.ln(height_line)
    return

def fill_cell_signature(pdf, key, value, wk, wv, align='C', border=1, font_k='宋体', font_size=15, font_v='hetang', print_no_key=False):
    flag_debug = True

    if flag_debug: print('fill_cell_signature')
    x, y = pdf.get_x(), pdf.get_y()

    if flag_debug: print(x, y)
    pdf.set_font(font_k, size=10)

    if print_no_key: wk = ''
    pdf.cell(wk, height_line, key, border=border, align=align)

    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_xy(pdf.get_x(), y+5)
    pdf.set_font(font_v, size=font_size)

    if flag_debug: print(pdf.get_x(), pdf.get_y())
    print_bold_text(pdf, pdf.get_x(), pdf.get_y(), value)

    # pdf.cell(wv, height_line, value, border=border)
    pdf.ln(height_line/2)
    return

def fill_cells(pdf, pair, wk, wv, align='C', border=1, new_line=True, print_no_key=False):
    pdf.set_font('宋体', size=10)
    x, y = pdf.get_x(), pdf.get_y()

    for label, value in pair.items():
        # print(label, value)
        lines = label.split('\n')
        n = len(lines)

        # Key
        pdf.cell(wk, height_line * n, '', border=border)
        for i, line in enumerate(lines):
            if print_no_key: line = ''
            pdf.set_xy(x, y + i * height_line)
            pdf.cell(wk, height_line, line, border=0, align=align)

        # Value
        pdf.set_xy(pdf.get_x(), pdf.get_y() - (n - 1) * height_line)
        pdf.cell(wv, height_line * n, value, border=border)

        if new_line:
            pdf.ln(height_line * n)
            x, y = pdf.get_x(), pdf.get_y()
        else:
            x += wk + wv
            y = pdf.get_y()
    if not new_line: pdf.ln(height_line*n)
    return x, y

def fill_signature_cell(pdf, string, width, height=height_line, print_no_key=False):
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    lines = string.split('\n')
    pdf.cell(width, height * len(lines), '', border=0)
    for i, line in enumerate(lines):
        if print_no_key: line = ''
        pdf.set_xy(start_x, start_y + i * height)
        pdf.cell(width, height, line, border=0, align='L')
    pdf.ln(height_line)

def add_signature_to_pdf(pdf, signature_image, x=50, y=50, width=80):
    img_width, img_height = signature_image.size
    aspect_ratio = img_height / img_width
    height = width * aspect_ratio
    # Add image to PDF
    pdf.image(signature_image, x=x, y=y, w=width, h=height)
    return