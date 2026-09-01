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
