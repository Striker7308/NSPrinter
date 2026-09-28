import pathlib
import warnings
import zxingcpp
from PIL import Image
from utils.decode import parse_invoice_qr, decode_qr
import io
import requests
import re
import pymupdf as fitz
from pdf2image import convert_from_bytes
import pandas as pd
import json


def get_invoice_url(orders_excel_fp):
    orders = pd.read_excel(orders_excel_fp)
    orders_invoice_url = {}

    # print(orders)
    # print(orders.columns)
    orders_urls = orders.iloc[:, [0, 4, 18]]
    # print(orders_urls)
    for order_id, _id, order_urls in orders_urls.itertuples(index=False, name=None):
        # print(order_id)
        # print(type(order_id))
        # print(order_urls)
        # print(type(order_urls))
        if type(order_urls) is not str: continue
        urls = order_urls.split('\n')
        # print('>>>>>>>>>')
        # print(urls[-1])
        orders_invoice_url[str(order_id)] = urls[-1]
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
        "发票号码": pat_no.group(1).strip() if pat_no else None,
        "invoice_date": pat_date.group(1).strip() if pat_date else None,
        "销售人": pat_buyer.group(1).strip() if pat_buyer else None,
        "buyer_id": buyer_id.strip() if buyer_id else None,
        "联系人": pat_seller.group(1).strip() if pat_seller else None,
        "证件号码": seller_id.strip() if seller_id else None,
        "商品名称": pat_item_row.group(1).strip() if pat_item_row else None,
        "amount_before_tax": pat_amt.group(1).strip() if pat_amt else None,
        "tax": pat_tax.group(1).strip() if pat_tax else None,
        "实付金额": pat_total.group(1).strip() if pat_total else None,
        "补贴金额": pat_subsidy.group(1).strip() if pat_subsidy else None,
        "收银金额": pat_actual_pay.group(1).strip() if pat_actual_pay else None,
        "联系人电话": pat_phone.group(1).strip() if pat_phone else None,
    }
    return res, txt, full_text


# def get_invoice(invoice_fp):
#     if invoice_fp is None or not pathlib.Path(invoice_fp).is_file():
#         warnings.warn('invoice file path does not exist, skip reading invoice file', UserWarning)
#         return {}
#     img = get_invoice_img_from_pdf(invoice_fp)
#     img.save(str(invoice_fp.parent)+'/invoice.png')
#     # img = Image.open(invoice_img_fp)
#     results = decode_qr(img)
#     invoice = parse_invoice_qr(results[0].text)
#     return invoice

def get_invoice_input(store, jiuxun, id, receipt, checking):
    if len(checking) == 0: return []
    invoice_input_list = [
        jiuxun['销方公司名称'] if checking['刷卡门店'] is True else 'xxxxxx销方公司名称错误xxxxxx',
        jiuxun['联系人'] if checking['联系人'] is True else 'xxxxxx联系人错误xxxxxx',
        str(id['num']) if checking['联系人'] is True else 'xxxxxx联系人错误xxxxxx',
        jiuxun['分类'],
        jiuxun['商品名称'],
        jiuxun['规格'],
        jiuxun['实付金额'],
    ]

    remark = '2026 年商洛市数码和智能产品购新, 购买方地址: '
    remark += store.get(jiuxun['销方公司名称'], {}).get('address', 'xxxxxx九讯云销方公司名称错误xxxxxx')+', '
    remark += '最终销售价格: '+ (jiuxun['实付金额']+'元, ' if checking['实付金额'] is True else 'xxxxxx实付金额错误xxxxxx, ')
    remark += '享受补贴资金数额: '+str(receipt.get('national_saving', 'xxxxxx小票错误xxxxxx'))+'元, '
    remark += '其他优惠金额: '+ (str(receipt.get('bank_saving', '0.00'))+'元, ' if len(receipt) > 0 else 'xxxxxx小票错误xxxxxx, ')
    remark += '消费者实际支付金额: '+str(receipt.get('pay', 'xxxxxx小票错误xxxxxx'))+'元, '
    remark += '消费者手机号: '+jiuxun['联系人电话']
    invoice_input_list.append(remark)

    return invoice_input_list


def get_invoice_input_(store, jiuxun, id, receipt):
    invoice_input_list = [
        jiuxun['销方公司名称'],
        jiuxun['联系人'],
        id['num'],
        jiuxun['分类'],
        jiuxun['商品名称'],
        jiuxun['规格'],
        jiuxun['实付金额'],
    ]

    remark = '2026 年商洛市数码和智能产品购新, 购买方地址: '
    remark += store[jiuxun['销方公司名称']]['address']+', '
    remark += '最终销售价格: '+jiuxun['实付金额']+'元, '
    remark += '享受补贴资金数额: '+receipt['national_saving']+'元, '
    remark += '其他优惠金额: '+receipt.get('bank_saving', '0.00')+'元, '
    remark += '消费者实际支付金额: '+receipt['pay']+'元, '
    remark += '消费者手机号: '+jiuxun['联系人电话']
    invoice_input_list.append(remark)

    return invoice_input_list


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
