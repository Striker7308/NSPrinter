import requests
from pdf2image import convert_from_path, convert_from_bytes
from fpdf import FPDF
# from pypdf import PdfReader, PdfWriter
import io

poppler_path = r"E:\poppler\poppler-26.09.0\Library\bin"

def pdf2img(pdf_url, fp):
    # download pdf bytes
    resp = requests.get(pdf_url, timeout=30)
    resp.raise_for_status()
    pdf_bytes = resp.content

    # convert bytes → list of PIL Image objects
    # poppler_path = r"E:\poppler-25.07.0\Library\bin"  # uncomment this line if poppler NOT in PATH

    img = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=poppler_path)[0]
    img.save(fp)

# def pdf2img(pdf_url):
#     # download pdf bytes
#     resp = requests.get(pdf_url, timeout=30)
#     resp.raise_for_status()
#     pdf_bytes = resp.content
#
#     # convert bytes → list of PIL Image objects
#     # poppler_path = r"E:\poppler-25.07.0\Library\bin"  # uncomment this line if poppler NOT in PATH
#
#     images = convert_from_bytes(
#         pdf_bytes,
#         dpi=300,
#         # poppler_path=poppler_path
#     )
#
#     # save each page
#     for idx, img in enumerate(images):
#         img.save(f"invoice_page_{idx + 1}.png")
#         print(f"Saved invoice_page_{idx + 1}.png")


def get_invoice_img_from_pdf(pdf_fp=r'C:\Users\cheng\Downloads\国补订单附件2026072116011\10219792（未审核）\dzfp_26612000001246692706_韩佳妮（个人）_20260627105212.pdf'):
    imgs = convert_from_path(pdf_fp)
    return imgs[0]

# def concat_fpdf_objects(*fpdf_objs: FPDF) -> bytes:
#     writer = PdfWriter()
#     for fpdf_inst in fpdf_objs:
#         buf = io.BytesIO(fpdf_inst.output())
#         r = PdfReader(buf)
#         for pg in r.pages:
#             writer.add_page(pg)
#     out_buf = io.BytesIO()
#     writer.write(out_buf)
#     return out_buf.getvalue()


def main():
    imgs = get_invoice_img_from_pdf()
    print(imgs[0])
    imgs[0].save('./../in.png')

if __name__ == '__main__':
    main()