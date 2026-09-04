import argparse
import argcomplete
import json
import pathlib
import time
from datetime import datetime, timedelta
import traceback
from PIL import Image, ImageDraw, ImageEnhance

from utils.filepath import find_invoice_fp, find_jiuxun_fp, find_id_fp, find_phone_fp, find_receipt_fp
from utils.io import dump_list_txt, load_list_txt
from id import get_id
from receipt import get_receipt, get_signature, get_rich_txt_by_Doubao
from sn import get_sn
from invoice import get_invoice, get_invoice_input
from jiuxun_info import get_jiuxun_info, get_product_detail, get_jiuxun
from store import load_store_config

def load_config(config_file="./config/content.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_det(dp='./imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)

    id_fp = find_id_fp(dp)
    phone_case_re_fp = '验机激活四码合一照片.jpg'
    # in_fp = find_invoice_fp(dp)

    id = get_id(id_fp)
    json.dump(id, open(dp.joinpath('id.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    phone = get_sn(find_phone_fp(dp))
    json.dump(phone, open(dp.joinpath('phone.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    receipt_img = Image.open(find_receipt_fp(dp))
    receipt = get_rich_txt_by_Doubao(receipt_img)
    # receipt, signature_img = get_receipt(dp+re_fp)
    json.dump(receipt, open(str(dp) + '/receipt.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

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
    return id, phone, receipt, invoice

def check_store_info(store, receipt, jiuxun):
    return {
        '刷卡门店': True if receipt.get("门店", '小票未识别到门店') == store.get(jiuxun.get('销方公司名称', '九讯云无销方公司名称'), {}).get('name', '九讯云无销方公司名称') else "小票门店 "+receipt.get("门店", '小票错误')+' != 九讯云门店 '+store.get(jiuxun.get('销方公司名称', '九讯云无销方公司名称'), {}).get('name', '九讯云无销方公司名称'),
        # '收货门店地址': True if jiuxun["customer_address"] == store[jiuxun['销方公司名称']]['address'] else "九讯云收货地址-"+jiuxun["customer_address"]+' 和 '+ '财务开票门店地址-'+store[jiuxun['销方公司名称']]['address'] + ' 不一致',
    } if len(receipt) > 0 else {'刷卡门店': '上传小票错误'}

def check_customer_info(id, receipt, jiuxun):
    return {
        # '顾客姓名': True if id["姓名"] == receipt["顾客签名"] else {'身份证姓名有误': id["姓名"], '小票签名有误': receipt["顾客签名"]},
        '联系人': True if id['name'] == jiuxun['联系人'] else '识别到 身份证照片 '+id['name']+' != 九讯云联系人 '+jiuxun['联系人']
    }

def check_payment(receipt, jiuxun):
    return {
        # '外部订单号': True if receipt['external_order_id'] == jiuxun['合同号'] else "小票外部订单号 "+receipt['external_order_id']+' 与 '+ '九讯云上外部订单号 '+jiuxun['合同号'] + ' 不一致',
        '实付金额': True if float(receipt['实收']) == float(jiuxun['实付金额']) else "识别到 小票总收银 "+str(receipt["实收"])+' 与 '+ '九讯云总收银 '+jiuxun['实付金额'] + ' 不一致',
        '政府补贴': True if float(receipt['national_saving']) == float(jiuxun['补贴金额']) else "识别到 小票国补 "+str(receipt["national_saving"])+' 与 '+ '九讯云国补 '+jiuxun['补贴金额'] + ' 不一致',
        '信用卡优惠': True,
        '实际支付': True if float(receipt['pay'])+float(receipt.get('bank_saving', 0)) == float(jiuxun['国补收银金额']) else '识别到 小票上顾客支付 '+str(receipt['pay'])+' + 银行优惠 '+str(receipt.get('bank_saving', '0'))+' 与 '+ '九讯云顾客支付 '+jiuxun['国补收银金额'] + ' 不一致',
    } if len(receipt) > 0 else {'实付金额': '未识别到小票', '政府补贴': '未识别到小票', '信用卡优惠': '未识别到小票', '实际支付': '未识别到小票'}

def check_merchandise_info(phone, receipt, jiuxun):
    match_sn = phone['SN'] == jiuxun['SN']
    match_sn = phone['SN'].replace('0', 'Q') == jiuxun['SN'] if not match_sn else match_sn
    return {
        'SN': match_sn if phone.get('SN', '') == jiuxun['SN'] else '识别到 手机屏显SN '+phone.get('SN', '')+' 与 九讯云上SN '+jiuxun['SN']+' 不一致',
        # 'SN有误': True if phone['SN'] == receipt['phone_info']['SN'] else "手机显示SN-"+phone['SN']+' 与 '+'小票显示SN-'+receipt['phone_info']['SN'] + ' 不一致',
        # 'SN': True if phone.get('SN', '') == jiuxun['SN'] else '识别到 手机屏显SN '+phone.get('SN', '')+' 与 九讯云上SN '+jiuxun['SN'] + ' 不一致',
        # 'IMEI1有误': True if phone['IMEI1'] == receipt['phone_info']['IMEI1'] else "手机显示IMEI1-"+phone['SN']+' ?= '+'小票显示IMEI1-'+receipt['phone_info']['SN'],
        'IMEI1': True if jiuxun['分类'] != '智能手机' or phone.get('IMEI1', '') == jiuxun['序列号'] else '手机屏显IMEI1 '+phone.get('IMEI1', '')+' 与 九讯云上IMEI1 '+jiuxun['序列号'] + ' 不一致',
        # 'IMEI2有误': True if phone['IMEI2'] == receipt['phone_info']['IMEI2'] else "手机显示SN-"+phone['IMEI2']+' ?= '+'小票显示SN-'+receipt['phone_info']['IMEI2'],
    } if len(phone) > 0 else {'SN': '未识别到机身串码及SN码截屏', 'IMEI1': '未识别到机身串码及SN码截屏'}

def check_one_day(day_dp):
    orders_dp = pathlib.Path(day_dp)
    if not orders_dp.exists(): return
    store = load_store_config()

    error_list = json.load(open(orders_dp.joinpath('error_list.json'), 'r', encoding='utf-8')) if orders_dp.joinpath('error_list.json').is_file() else {}
    for dp in orders_dp.iterdir():
        order_id_dp = dp.name.split('（')[0]
        # if not dp.is_dir() or error_list.get(order_id_dp, None) == 'check':
        #     print(dp, 'check')
        #     continue

        if not dp.is_dir():
            continue
        if order_id_dp != '10232878':
            print(dp, 'ignore')
            continue

        print(dp, 'checking')

        try:
            '''read jiuxun first'''
            jiuxun = get_jiuxun(dp)

            '''read data multimodality'''
            id, phone, receipt, invoice = get_det(dp)

            '''check data match by rule'''
            checking = check_store_info(store, receipt, jiuxun)
            checking = {**checking, **check_customer_info(id, receipt, jiuxun)}
            checking = {**checking, **check_payment(receipt, jiuxun)}
            checking = {**checking, **check_merchandise_info(phone, receipt, jiuxun)}

            '''format output info'''
            json.dump(checking, open(str(dp)+'/checking.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

            '''format error info'''
            error_info = {k: v for k, v in checking.items() if v is not True}
            error_list[jiuxun['订单号']] = 'check' if len(error_info) == 0 else {**{'seller': jiuxun['销售人']}, **error_info}

        except Exception as e:
            print(order_id_dp, ' checking error:', e)
            traceback.print_exc()
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    json.dump(error_list, open(orders_dp.joinpath('error_list.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return

def verify_all_(day=0):
    root_dp = pathlib.Path('E:/share/')
    for dp in root_dp.iterdir():
        if not dp.is_dir(): continue
        date = (datetime.now()+timedelta(days=day)).strftime("%Y%m%d")
        print(date)
        dp_day = dp.joinpath('国补订单附件'+date)
        check_one_day(dp_day)
    return

def verify_all(dp='E:/share/'):
    # root_dp = pathlib.Path('E:/share/')
    # date = (datetime.now()+timedelta(days=day)).strftime("%Y%m%d")
    # dp_day = root_dp.joinpath('国补订单附件'+date)

    dp_day = pathlib.Path(dp)
    print(dp_day.is_dir())
    if not dp_day.is_dir():
        print(dp_day, 'not exist')
        return
    print('checking', dp_day)
    check_one_day(dp_day)
    return

def main():
    # root_dp = 'E:/share/BaoTongShi/国补订单附件20260814'
    # root_dp = 'E:/share/NingZhiYuan/国补订单附件20260815'
    # root_dp = 'E:/share/YouShangDa/国补订单附件20260815'
    # root_dp = 'E:/share/HengGuo/国补订单附件20260815'
    # root_dp = 'E:/share/HengTan/国补订单附件20260815'
    # check_one_day(root_dp)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--date_offset", type=int, help="offset day: 0 = today, -1 = yesterday, negative numbers for past days")
    # argcomplete.autocomplete(parser)  # enable tab complete hook
    # args = parser.parse_args()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    argcomplete.autocomplete(parser)  # enable tab complete hook
    args = parser.parse_args()

    verify_all(args.dir)

    # print('verify.py called at', datetime.now())
    return


if __name__ == '__main__':
    main()
