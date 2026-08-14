import json
import pathlib
import time
from PIL import Image, ImageDraw, ImageEnhance

from utils.filepath import find_invoice_fp, find_jiuxun_fp, find_id_fp

from id import get_id
from receipt import get_receipt, get_signature, get_rich_txt_by_Doubao
from sn import get_sn
from invoice import get_invoice
from jiuxun_info import get_jiuxun_info, get_product_detail
from store import load_store_config

def load_config(config_file="./config/content.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_det(dp='./imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)

    id_fp = find_id_fp(dp)
    phone_case_re_fp = '验机激活四码合一照片.jpg'
    re_fn = '销售小票及刷卡小票.jpg'
    phone_fn = '机身串码及SN码截屏.jpg'
    jiuxun_fp = find_jiuxun_fp(dp)
    # in_fp = find_invoice_fp(dp)

    id = get_id(id_fp)
    json.dump(id, open(dp.joinpath('id.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    phone = get_sn(dp.joinpath(phone_fn))
    json.dump(phone, open(dp.joinpath('phone.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    receipt_img = Image.open(dp.joinpath(re_fn))
    receipt = get_rich_txt_by_Doubao(receipt_img)
    # receipt, signature_img = get_receipt(dp+re_fp)
    # json.dump(receipt, open(str(dp) + '/receipt.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    jiuxun = get_jiuxun_info(jiuxun_fp)

    invoice = {}
    # invoice = get_invoice(in_fp)

    # print('id')
    # print(json.dumps(id, indent=2, ensure_ascii=False))
    # print('phone')
    # print(json.dumps(phone, indent=2, ensure_ascii=False))
    # print('receipt')
    # print(json.dumps(receipt, indent=2, ensure_ascii=False))
    # print('invoice')
    # print(json.dumps(invoice, indent=2, ensure_ascii=False))
    # print()
    return id, phone, receipt, invoice, jiuxun

def check_store_info(store, receipt, jiuxun):
    return {
        '刷卡门店': True if receipt["门店"] == store[jiuxun['销方公司名称']]['name'] else "小票门店-"+receipt["门店"]+' != '+ '九讯云门店-'+store[jiuxun['销方公司名称']]['name'],
        # '收货门店地址': True if jiuxun["customer_address"] == store[jiuxun['销方公司名称']]['address'] else "九讯云收货地址-"+jiuxun["customer_address"]+' != '+ '财务开票门店地址-'+store[jiuxun['销方公司名称']]['address'],
    }

def check_customer_info(id, receipt, jiuxun):
    return {
        # '顾客姓名': True if id["姓名"] == receipt["顾客签名"] else {'身份证姓名有误': id["姓名"], '小票签名有误': receipt["顾客签名"]},
        '顾客姓名': True if id['name'] == jiuxun['联系人'] == jiuxun['发票抬头'] else {'身份证照片': id['name'], '发票联系人': jiuxun['联系人'], '发票抬头': jiuxun['发票抬头']},
    }

def check_payment(receipt, jiuxun):
    return {
        '外部订单号': True if receipt['external_order_id'] == jiuxun['合同号'] else "小票外部订单号-"+receipt['external_order_id']+' != '+ '九讯云上外部订单号-'+jiuxun['合同号'],
        '实付金额': True if receipt['实收'] == jiuxun['实付金额'] else "小票门店-"+receipt["门店"]+' != '+ '九讯云上开票门店-'+jiuxun['实付金额'],
        '政府补贴': True if float(receipt['national_saving']) == float(jiuxun['补贴金额']) else "小票上国补-"+receipt["national_saving"]+' != '+ '九讯云上国补-'+jiuxun['补贴金额'],
        '信用卡优惠': True,
        '实际支付': True if float(receipt['pay'])+float(receipt.get('bank_saving', 0)) == float(jiuxun['国补收银金额']) else '小票上顾客支付-'+receipt['pay']+' + 银行优惠-'+receipt.get('bank_saving', 0)+' != '+ '九讯云上顾客支付-'+jiuxun['国补收银金额'],
    }

def check_merchandise_info(phone, receipt, jiuxun):
    phone['SN'] = jiuxun['SN']
    return {
        # 'SN有误': True if phone['SN'] == receipt['phone_info']['SN'] else "手机显示SN-"+phone['SN']+' != '+'小票显示SN-'+receipt['phone_info']['SN'],
        'SN': True if phone['SN'] == jiuxun['SN'] else '手机显示SN-'+phone['SN'] +' != '+ '九讯云上SN-'+jiuxun['SN'],
        # 'IMEI1有误': True if phone['IMEI1'] == receipt['phone_info']['IMEI1'] else "手机显示IMEI1-"+phone['SN']+' ?= '+'小票显示IMEI1-'+receipt['phone_info']['SN'],
        'IMEI1': True if phone['IMEI1'] == jiuxun['序列号'] else '手机显示IMEI1-'+phone['IMEI1'] +' ?= '+ '九讯云上IMEI1-'+jiuxun['序列号'],
        # 'IMEI2有误': True if phone['IMEI2'] == receipt['phone_info']['IMEI2'] else "手机显示SN-"+phone['IMEI2']+' ?= '+'小票显示SN-'+receipt['phone_info']['IMEI2'],
    }

def main():
    root_dp = './imgs/hengtan/国补订单附件20260812/'
    # root_dp = './imgs/国补订单附件20260730/'
    # root_dp = './imgs/国补订单附件2026072210210/'
    # root_dp = './imgs/国补订单附件-rongyao/'
    # root_dp = './imgs/国补订单附件-qijian/'
    # root_dp = './imgs/国补订单附件-pinpai/'
    # root_dp = './imgs/国补订单附件-beiting/'
    # root_dp = './imgs/国补订单附件-pingguo/'
    root_dp = pathlib.Path(root_dp)
    store = load_store_config()

    status_list = {}
    error_list = {}

    for dp in root_dp.iterdir():
        if not dp.is_dir() or (dp.joinpath('status.json').is_file() and json.load(open(str(dp)+'/status.json', 'r', encoding='utf-8')) == 1):
            print(dp, 'checked')
            continue
        status = 1

        '''read data multimodality'''
        id, phone, receipt, invoice, jiuxun = get_det(dp)

        '''check data match by rule'''
        check = check_store_info(store, receipt, jiuxun)
        check = {**check, **check_customer_info(id, receipt, jiuxun)}
        # check_payment(receipt, jiuxun)
        check = {**check, **check_merchandise_info(phone, receipt, jiuxun)}

        '''format output info'''
        order_id = {
            'order_id': jiuxun['订单号'],
            'seller': jiuxun['销售人'],
        }
        json.dump({**order_id, **check}, open(str(dp)+'/check.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

        '''format error info'''
        error_info = {k: v for k, v in check.items() if v is not True}
        if len(error_info) != 0:
            status = 0
            error_list[jiuxun['订单号']] = {**order_id, **error_info}
        json.dump(status, open(str(dp)+'/status.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

        # local_time = time.localtime(time.time())
        # local_time_str = time.strftime("%Y%m%d", local_time)
        # print(dp, 'current time:', local_time_str)  # date string: 2026‑08‑12
        # break
        # in_fp = find_invoice_fp(dp)
        # invoice = get_invoice(in_fp)
        # jiuxun_fp = find_jiuxun_fp(dp)
        # jiuxun = get_jiuxun_info(jiuxun_fp)
        #
        # config = load_config()
        # set_config_from_det(config, jiuxun, invoice, store)
        # # print(json.dumps(config, indent=2, ensure_ascii=False))
        #
        # # signature_img = get_signature()
        #
        # '''build tax data'''
        # tax = get_tax_json(jiuxun, invoice, store)
        # json.dump(tax, open(str(dp)+'/check.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump(error_list, open(str(root_dp) + '/error_list.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return


if __name__ == '__main__':
    main()
