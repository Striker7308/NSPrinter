from pdf2image import convert_from_path

def get_invoice_img_from_pdf(pdf_fp=r'C:\Users\cheng\Downloads\国补订单附件2026072116011\10219792（未审核）\dzfp_26612000001246692706_韩佳妮（个人）_20260627105212.pdf'):
    imgs = convert_from_path(pdf_fp)
    return imgs[0]

def main():
    imgs = get_invoice_img_from_pdf()
    print(imgs[0])
    imgs[0].save('./../in.png')

if __name__ == '__main__':
    main()