import copy
import pathlib
import warnings
import zxingcpp
from PIL import Image
from utils.decode import parse_invoice_qr, decode_qr
from utils.pdf import get_invoice_img_from_pdf

def get_invoice(invoice_fp):
    if invoice_fp is None or not pathlib.Path(invoice_fp).is_file():
        warnings.warn('invoice file path does not exist, skip reading invoice file', UserWarning)
        return {}
    img = get_invoice_img_from_pdf(invoice_fp)
    img.save(str(invoice_fp.parent)+'/invoice.png')
    # img = Image.open(invoice_img_fp)
    results = decode_qr(img)
    invoice = parse_invoice_qr(results[0].text)
    return invoice

def test_invoice():
    print(f"支持的格式: {zxingcpp.barcode_formats_list()}")

    image_file = './imgs/0/invoice.jpg'
    results = decode_qr(image_file)
    invoice = parse_invoice_qr(results[0].text)
    print(type(invoice))
    print(invoice)
    print(invoice['invoice_code'])
    print(invoice['invoice_number'])
    return


def main():
    test_invoice()


if __name__ == '__main__':
    main()
