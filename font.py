import os
import json
import pathlib
from tkinter.font import names

import numpy
from fpdf import FPDF
import random

def load_font_config(config_file="./config/font.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_fonts_info():
    fontname_prob = load_font_config()
    keys = list(fontname_prob.keys())
    weights = numpy.asarray(list(fontname_prob.values()))
    weights /= weights.sum()

    # pick one sample
    for key, weight in zip(keys, weights):
        print(key, weight)

def get_a_fonts():
    fontname_prob = load_font_config()
    keys = list(fontname_prob.keys())
    weights = list(fontname_prob.values())
    # pick one sample
    selected = random.choices(keys, weights=weights, k=1)[0]
    return selected

def print_bold_text(pdf, x, y, text, offset=0.12):
    space_x, space_y = 3, 10
    rand_x, rand_y = 1, 0.3
    for t in text:
        """模拟加粗，offset越大越粗"""
        pdf.text(x-offset, y, t)
        pdf.text(x+offset, y, t)
        pdf.text(x, y-offset*0.6, t)
        pdf.text(x, y+offset*0.6, t)
        pdf.text(x, y, t) # 中心原色

        rand_x_ = random.uniform(-rand_x, rand_x)
        rand_y_ = random.uniform(-rand_y, rand_y)
        x += space_x + rand_x_
        y += rand_y_
        print(x, y)

def test_all_font():
    fontname_prob = load_font_config()
    font_dp = './fonts/'

    pdf = FPDF()
    pdf.add_page()

    y = 10
    for fontname, prob in fontname_prob.items():
        font_fp = font_dp + fontname
        print(font_fp)
        name = fontname.split('.')[0]
        pdf.add_font(name, '', font_fp)
        pdf.set_font(name, size=15)
        pdf.set_xy(20, y)
        # pdf.cell(0, 20, 'start here', ln=True)
        pdf.cell(0, 20, f'{name}: 这是手写字体效果 13641617308 ', ln=True)

        pdf.set_xy(20, pdf.get_y())
        print_bold_text(pdf, pdf.get_x(), pdf.get_y(), '13641617308 2024-08-01 16:40:15')
        y += 15
    pdf.output('./test_all_fonts.pdf')
    print("✅ PDF created: test_all_fonts.pdf")

def test_random_font():
    get_all_fonts_info()
    font_dp = './fonts/'

    pdf = FPDF()

    pdf.add_page()

    y = 10
    for i in range(50):
        fontname = get_a_fonts()
        font_fp = font_dp + fontname
        print(font_fp)
        name = fontname.split('.')[0]
        pdf.add_font(name, '', font_fp)
        pdf.set_font(name, size=15)
        pdf.set_xy(20, y)
        # pdf.cell(0, 20, 'start here', ln=True)
        pdf.cell(0, 20, f'{name}: 这是手写字体效果 13641617308 ', ln=True)
        # pdf.cell(0, 20, f'{name}: 这是手写字体效果 富兰克林 麦克 崔佛 ', ln=True)
        y += 10
    pdf.output('./test_all_fonts.pdf')
    print("✅ PDF created: test_all_fonts.pdf")

def main():
    test_all_font()


if __name__ == '__main__':
    main()