import json
import os.path
import pathlib

from fpdf import FPDF
from utils.cell import fill_signature_cell, fill_cells, fill_cell, fill_cell_signature
from utils.filepath import find_invoice_fp, find_jiuxun_fp

from id import get_id
from receipt import get_receipt, get_signature
from sn import get_sn
from invoice import get_invoice
from jiuxun_info import get_jiuxun_info, get_product_detail
from store import load_store_config
from font import get_a_fonts
from tax import get_tax_json

def load_config(config_file="./config/content.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# def get_det(dp='./imgs/10219792（未审核）/'):
#     # id_fp = '/id.jpg'
#     # re_fp = '/re.jpg'
#     # sn_fp = '/sn.jpg'
#     # in_fp = '/in.jpg'
#     id_fp = '/身份证照片.jpg'
#     re_fp = '/销售小票及刷卡小票.jpg'
#     sn_fp = '/机身串码及SN码截屏.jpg'
#     in_fp = find_invoice_fp(dp)
#
#     id = get_id(dp+id_fp)
#     # sn = get_sn(dp+sn_fp)
#     receipt, signature_img = get_receipt(dp+re_fp)
#     invoice = get_invoice(in_fp)
#
#     print('id')
#     print(json.dumps(id, indent=2, ensure_ascii=False))
#     # print('sn')
#     # print(json.dumps(sn, indent=2, ensure_ascii=False))
#     print('receipt')
#     print(json.dumps(receipt, indent=2, ensure_ascii=False))
#     print('invoice')
#     print(json.dumps(invoice, indent=2, ensure_ascii=False))
#     print()
#     return id, receipt, invoice, signature_img

def create_pdf_from_config(config, signature_img):
    """write pdf using config parameters"""
    print_no_key = False

    '''size'''
    width = 150
    height_line = 8
    board = True

    '''PDF'''
    # 简化版示例
    pdf = FPDF()
    pdf.add_page()
    print('pdf.h', pdf.h)
    print('pdf.w', pdf.w)

    # load hand writing font
    handwrite_font_fn = get_a_fonts()
    # handwrite_font_fn = 'ProperScript-Regular.ttf'
    handwrite_font_name = handwrite_font_fn.split('.')[0]

    print('using handwrite ', handwrite_font_fn)
    pdf.add_font('黑体', '', 'C:/Windows/Fonts/simhei.ttf')
    pdf.add_font('宋体', '', 'C:/Windows/Fonts/simsun.ttc')
    pdf.add_font(handwrite_font_name, '', './fonts/'+handwrite_font_fn)

    # pdf.add_font('ChillZhuoKai', '', './fonts/ChillZhuoKai.ttf')
    # pdf.add_font('slideyouran', '', './fonts/slideyouran-Regular.ttf')
    # pdf.add_font('hetang', '', './fonts/荷塘月色手写体+Regular.ttf')

    # set margin
    pdf.set_left_margin(30)
    if print_no_key: board = 0

    # title
    pdf.ln(10)
    pdf.set_font('黑体', size=18)
    pdf.cell(width, 10, config['title'], align='C')
    pdf.ln(15)

    # info
    width_info_key = 40
    fill_cells(pdf, config['fields'], width_info_key, width - width_info_key, border=board, print_no_key=print_no_key)

    # payment
    width_pay_key = 40
    fill_cells(pdf, config['payment1'], width_info_key, width / 2 - width_pay_key, k_align='C', v_align='C', border=board, new_line=False, print_no_key=print_no_key)
    fill_cells(pdf, config['payment2'], width_info_key, width / 2 - width_pay_key, k_align='C', v_align='C', border=board, new_line=False, print_no_key=print_no_key)

    start_x, start_y = pdf.get_x(), pdf.get_y()
    pdf.cell(width, 70, '', border=board)
    pdf.set_xy(start_x, start_y)

    # declare
    pdf.set_font('黑体', size=11)
    # pdf.set_font('花体', size=11)
    fill_signature_cell(pdf, config['declaration'], width, height_line, print_no_key)
    pdf.ln(10)

    # sign
    width_sign_key = 90
    fill_cell_signature(pdf, '消费者姓名:', '', width_sign_key, width - width_sign_key, align='R', border=0, font_v=handwrite_font_name)
    fill_cell_signature(pdf, '消费者电话:', config['signature']['消费者电话:'], width_sign_key, width - width_sign_key, align='R', border=0, font_v=handwrite_font_name)
    fill_cell_signature(pdf, '签收时间:', config['signature']['签收时间:'], width_sign_key, width - width_sign_key, align='R', border=0, font_v=handwrite_font_name)

    # config['signature'].pop('消费者姓名:')
    print(config['signature'])
    # fill_cells(pdf, config['signature'], width_sign_key, width - width_sign_key, align='R', border=0)
    # pdf.image(signature_img)

    width_order_id_key = 150

    start_x, start_y = pdf.get_x(), pdf.get_y()
    pdf.set_xy(start_x, start_y+5)
    fill_cell(pdf, '', config['selling_store_id']+'-'+config['seller'], width_order_id_key, width - width_order_id_key, align='R', border=0, font_v='黑体', font_size=10)
    fill_cell(pdf, '', config['selling_ord_id'], width_order_id_key, width - width_order_id_key, align='R', border=0, font_v='黑体',font_size=10)

    return pdf


def set_config_from_det(config, jiuxun, invoice, store):
    if jiuxun['分类'] == '笔记本电脑': config["title"] = '2026年陕西省家电以旧换新补贴确认书'
    config["fields"]['销售企业名称'] = jiuxun['销方公司名称']

    config["fields"]['销售企业名称'] = jiuxun['销方公司名称']
    config["fields"]['销售门店名称'] = store.get(jiuxun['销方公司名称'], {}).get('name', '未登记')
    config["fields"]["外部订单号\n（签购单内查找）"] = jiuxun['合同号']
    config["fields"]["发票号码"] = invoice.get('invoice_number', '')

    config["fields"]["品牌+类型+型号\n如华为Mate70 12GB+512GB"] = get_product_detail(jiuxun)

    config["fields"]["SN码\n（家电及数码均需提供）"] = jiuxun['SN']

    config["fields"]["收货地址\n（具体至门牌号）"] = store.get(jiuxun['销方公司名称'], {}).get('address', '未登记')+'(自提)'

    config["payment1"]["最终销售价格\n（POS单上原始金额）"] = jiuxun['实付金额']
    config["payment1"]["享受补贴资金数额\n（政府补贴金额）"] = jiuxun['补贴金额']
    config["payment2"]["其他优惠金额\n（如银行等补贴，无填0）\n"] = str(0)
    config["payment2"]["消费者实际支付金额\n（POS单上银联二维码\n支付金额）"] = jiuxun['国补收银金额']
    # config["payment1"]["最终销售价格\n（POS单上原始金额）"] = receipt['金额']
    # config["payment1"]["享受补贴资金数额\n（政府补贴金额）"] = str(receipt['saving'])
    # config["payment2"]["其他优惠金额\n（如银行等补贴，无填0）\n"] = str(extra_saving)
    # config["payment2"]["消费者实际支付金额\n（POS单上银联二维码\n支付金额）"] = receipt['pay']

    config["signature"]["消费者姓名:"] = jiuxun['联系人']
    # config["signature"]["消费者姓名:"] = customer_id["姓名"]
    config["signature"]["消费者电话:"] = jiuxun['联系人电话']
    config["signature"]["签收时间:"] = jiuxun['交易时间'].split(' ')[0]

    config["selling_store_id"] = jiuxun['门店代码']
    config["seller"] = jiuxun['销售人']
    config["selling_ord_id"] = jiuxun['订单号']
    return config

# def set_config_from_det_(config, customer_id, receipt, invoice, jiuxun):
#     extra_saving = float(receipt['金额'])-float(receipt['saving'])-float(receipt['pay'])
#     # extra_saving = float(receipt['金额'])-float(receipt["第三方优惠说明"]["线下优惠"])-float(receipt["第三方优惠说明"]["银联二维码支付"])
#
#     print('extra_saving', extra_saving)
#     config["fields"]["外部订单号\n（签购单内查找）"] = receipt['external_order_id']
#     config["fields"]["发票号码"] = invoice['invoice_number']
#
#     config["fields"]["品牌+类型+型号\n如华为Mate70 12GB+512GB"] = get_product_detail(jiuxun)
#     # config["fields"]["品牌+类型+型号\n如华为Mate70 12GB+512GB"] = jiuxun['商品名称']
#     # config["fields"]["品牌+类型+型号\n如华为Mate70 12GB+512GB"] = receipt['phone_info']['name']
#
#     config["fields"]["SN码\n（家电及数码均需提供）"] = jiuxun['SN']
#     # config["fields"]["SN码\n（家电及数码均需提供）"] = sn['SN']
#
#     config["payment1"]["最终销售价格\n（POS单上原始金额）"] = receipt['金额']
#     config["payment1"]["享受补贴资金数额\n（政府补贴金额）"] = str(receipt['saving'])
#     config["payment2"]["其他优惠金额\n（如银行等补贴，无填0）\n"] = str(extra_saving)
#     config["payment2"]["消费者实际支付金额\n（POS单上银联二维码\n支付金额）"] = receipt['pay']
#
#     config["signature"]["消费者姓名:"] = jiuxun["联系人"]
#     # config["signature"]["消费者姓名:"] = customer_id["姓名"]
#     config["signature"]["消费者电话:"] = jiuxun["联系人电话"]
#     config["signature"]["签收时间:"] = receipt["时间"]
#     return config

def main():
    root_dp = './imgs/国补订单附件20260806/'
    # root_dp = './imgs/国补订单附件2026072210210/'
    # root_dp = './imgs/国补订单附件-lv/'
    # root_dp = './imgs/国补订单附件-rongyao/'
    # root_dp = './imgs/国补订单附件-qijian/'
    # root_dp = './imgs/国补订单附件-pinpai/'
    # root_dp = './imgs/国补订单附件-beiting/'
    # root_dp = './imgs/国补订单附件-pingguo/'
    root_dp = pathlib.Path(root_dp)

    store = load_store_config()

    for dp in root_dp.iterdir():
        if not dp.is_dir(): continue
        # dp = './imgs/国补订单附件2026072119282/10221431（未审核）/'
        # dp = './imgs/10219792（未审核）'
        # dp = './imgs/国补订单附件2026072210210/10224861（未审核）/'
        # dp = './imgs/国补订单附件-pingguo/10221921（未审核）/'

        # customer_id, receipt, invoice, signature_img = get_det(dp)
        in_fp = find_invoice_fp(dp)
        invoice = get_invoice(in_fp)
        jiuxun_fp = find_jiuxun_fp(dp)
        jiuxun = get_jiuxun_info(jiuxun_fp)

        config = load_config()
        set_config_from_det(config, jiuxun, invoice, store)
        # print(json.dumps(config, indent=2, ensure_ascii=False))

        # signature_img = get_signature()
        pdf = create_pdf_from_config(config, None)
        # print(pdf)
        pdf.output(str(dp)+'/output.pdf')

        '''build tax data'''
        tax = get_tax_json(jiuxun, invoice, store)
        json.dump(tax, open(str(dp)+'/tax.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    return


if __name__ == '__main__':
    main()
