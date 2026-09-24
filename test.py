import io
import requests
import re
import pymupdf as fitz
from pdf2image import convert_from_bytes
import pandas as pd
import json
pdf_url = "https://img.9xun.com/newstatic/40457/3573293f5bfcf7df.pdf"
orders_excel_fp = 'E:/share/国补订单附件20260922-upload_test/国补订单明细.xlsx'


def get_invoice_url(orders_excel_fp):
    orders = pd.read_excel(orders_excel_fp)
    orders_invoice_url = {}

    # print(orders)
    # print(orders.columns)
    orders_urls = orders.iloc[:, [0, 18]]
    # print(orders_urls)
    for order_id, order_urls in orders_urls.itertuples(index=False, name=None):
        # print(order_id)
        # print(type(order_id))
        # print(order_urls)
        # print(type(order_urls))
        if type(order_urls) is not str: continue
        urls = order_urls.split('\n')
        # print('>>>>>>>>>')
        # print(urls[-1])
        orders_invoice_url[order_id] = urls[-1]
    return orders_invoice_url


def extract_invoice(pdf_link):
    resp = requests.get(pdf_link, timeout=30)
    resp.raise_for_status()
    doc = fitz.open(stream=io.BytesIO(resp.content), filetype="pdf")

    full_text = ""
    for page in doc:
        full_text += page.get_text(sort=True)
    doc.close()

    txt = re.sub(r"\s+", " ", full_text)
    pat_code = re.search(r"发票代码\s*[:：]?\s*(\d+)", txt)
    pat_no = re.search(r"发票号码\s*[:：]?\s*(\d+)", txt)
    pat_date = re.search(r"开票日期\s*[:：]?\s*(\d{4}年\d{1,2}月\d{1,2}日)", txt)

    # Buyer: capture everything after 购 ...名称： until "统一社会信用代码"
    pat_buyer = re.search(r"购.*?名称[:：]\s*(.*?)\s*销.*?名称", txt)
    # pat_buyer = re.search(r"购.*?名称[:：]\s*(.*?)\s*统一社会信用代码", txt)
    buyer_id = ''

    # Seller: capture everything after 销 ...名称： until "统一社会信用代码"
    pat_seller = re.search(r"销.*?名称[:：]\s*(.*?)\s*买 售", txt)
    # pat_seller = re.search(r"销.*?名称[:：]\s*(.*?)\s*统一社会信用代码", txt)
    seller_id = ''

    id_matches = list(re.finditer(
        r"统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18})",
        full_text
    ))
    for id_match in id_matches:
        code = id_match.group(1)
        if code.isnumeric():
            buyer_id = code
        else:
            seller_id = code

    pat_total = re.search(r"价税合计.*?¥\s*([0-9.]+)", txt)
    pat_tax = re.search(r"合 计 ¥[\d.]+\s*¥\s*([0-9.]+)", txt)
    pat_amt = re.search(r"合 计 ¥\s*([0-9.]+)\s*¥[\d.]+", txt)

    pat_subsidy = re.search(r"补贴资金数额[:：]\s*([0-9.]+)", txt)
    pat_actual_pay = re.search(r"消费者实际支付金额[:：]\s*([0-9.]+)", txt)
    pat_phone = re.search(r"消费者手机号[:：]\s*(\d{11})", txt)
    pat_item_row = re.search(r"\*移动通信设备\*([^¥]+?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+%)", txt)

    res = {
        "invoice_code": pat_code.group(1).strip() if pat_code else None,
        "invoice_number": pat_no.group(1).strip() if pat_no else None,
        "invoice_date": pat_date.group(1).strip() if pat_date else None,
        "buyer_name": pat_buyer.group(1).strip() if pat_buyer else None,
        "buyer_id": buyer_id.strip() if buyer_id else None,
        "seller_name": pat_seller.group(1).strip() if pat_seller else None,
        "seller_id": seller_id.strip() if seller_id else None,
        "good_name": pat_item_row.group(1).strip() if pat_item_row else None,
        "amount_before_tax": pat_amt.group(1).strip() if pat_amt else None,
        "tax": pat_tax.group(1).strip() if pat_tax else None,
        "total_amount": pat_total.group(1).strip() if pat_total else None,
        "subsidy": pat_subsidy.group(1).strip() if pat_subsidy else None,
        "actual_payment": pat_actual_pay.group(1).strip() if pat_actual_pay else None,
        "buyer_phone": pat_phone.group(1).strip() if pat_phone else None,
    }
    return res, txt, full_text


def pdf2img(pdf_url):
    # download pdf bytes
    resp = requests.get(pdf_url, timeout=30)
    resp.raise_for_status()
    pdf_bytes = resp.content

    # convert bytes → list of PIL Image objects
    # poppler_path = r"E:\poppler-25.07.0\Library\bin"  # uncomment this line if poppler NOT in PATH

    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
        # poppler_path=poppler_path
    )

    # save each page
    for idx, img in enumerate(images):
        img.save(f"invoice_page_{idx + 1}.png")
        print(f"Saved invoice_page_{idx + 1}.png")

    # images[0] is PIL Image, you can pass it to OCR later if needed


if __name__ == "__main__":
    # pdf2img()
    orders_invoice_url = get_invoice_url(orders_excel_fp)
    print(orders_invoice_url)
    inv, txt, full_text = extract_invoice(pdf_url)
    print(json.dumps(inv, indent=2, ensure_ascii=False))
    # print("==== Parsed ====")
    # for k, v in inv.items():
    #     if k not in ("raw_text", "clean_text"):
    #         print(f"{k}: {v}")
    #
    # with open("invoice_clean.txt","w",encoding="utf-8") as f:
    #     f.write(inv["clean_text"])
