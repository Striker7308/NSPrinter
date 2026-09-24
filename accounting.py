import argparse
import argcomplete
import json
import pathlib
import time
import traceback
from PIL import Image, ImageDraw, ImageEnhance
from datetime import datetime, timedelta

from utils.filepath import find_invoice_fp, find_jiuxun_fp, find_id_fp
from utils.io import dump_list_txt, load_list_txt
from invoice import get_invoice_input
from jiuxun_info import get_jiuxun_info, get_product_detail
from store import load_store_config


def get_det_locally(dp='./imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    id_json_fn = 'id.json'
    phone_json_fn = 'phone.json'
    re_json_fn = 'receipt.json'
    jiuxun_fp = find_jiuxun_fp(dp)

    id = json.load(open(dp.joinpath(id_json_fn), 'r', encoding='utf-8')) if dp.joinpath(id_json_fn).is_file() else {}
    phone = json.load(open(dp.joinpath(phone_json_fn), 'r', encoding='utf-8')) if dp.joinpath(phone_json_fn).is_file() else {}
    receipt = json.load(open(dp.joinpath(re_json_fn), 'r', encoding='utf-8')) if dp.joinpath(re_json_fn).is_file() else {}
    jiuxun = get_jiuxun_info(jiuxun_fp)

    invoice = {}
    # invoice = get_invoice(in_fp)
    return id, phone, receipt, invoice, jiuxun

# def get_invoice_one_store_day(orders_dp):
#     orders_dp = pathlib.Path(orders_dp)
#     if not orders_dp.exists(): return
#
#     store = load_store_config()
#     invoice_inputs_dict = []
#
#     for dp in orders_dp.iterdir():
#         if not dp.is_dir():
#             continue
#         print('get invoice input from', dp)
#
#         '''read det data'''
#         id, phone, receipt, invoice, jiuxun = get_det_locally(dp)
#
#         '''check data match by rule'''
#         checking = json.load(open(dp.joinpath('checking.json'), 'r', encoding='utf-8')) if dp.joinpath('checking.json').is_file() else {}
#
#         '''format output info'''
#         invoice_inputs = get_invoice_input(store, jiuxun, id, receipt, checking)
#         json.dump(invoice_inputs, open(dp.joinpath('invoice_inputs.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
#
#         '''format output info'''
#         invoice_inputs_dict += [jiuxun['订单号']] + invoice_inputs + ['>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'] + ['']
#         print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#
#     dump_list_txt(invoice_inputs_dict, str(orders_dp.joinpath('invoice_inputs_list.txt')))
#     return

def get_invoice_one_company_day(orders_dp):
    orders_dp = pathlib.Path(orders_dp)
    if not orders_dp.exists(): return

    store = load_store_config()
    invoice_inputs_per_company = {}

    for dp in orders_dp.iterdir():
        if not dp.is_dir():
            continue
        print('get invoice input from', dp)

        '''read det data'''
        id, phone, receipt, invoice, jiuxun = get_det_locally(dp)

        '''check data match by rule'''
        checking = json.load(open(dp.joinpath('checking.json'), 'r', encoding='utf-8')) if dp.joinpath('checking.json').is_file() else {}

        '''format output info'''
        invoice_inputs = get_invoice_input(store, jiuxun, id, receipt, checking)
        json.dump(invoice_inputs, open(dp.joinpath('invoice_inputs.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

        '''format output info'''
        invoice_inputs_per_company[jiuxun['销方公司名称']] = invoice_inputs_per_company.get(jiuxun['销方公司名称'],[])+[jiuxun['订单号']]+invoice_inputs+['>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>']+['']
        # invoice_inputs_dict += [jiuxun['订单号']] + invoice_inputs + ['>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'] + ['']
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    for company, invoice_inputs in invoice_inputs_per_company.items():
        dump_list_txt(invoice_inputs, str(orders_dp.joinpath(company+'invoice_inputs_list.txt')))
    return

def get_invoice_all_store_one_day(dp):
    # root_dp = pathlib.Path('E:/share/')
    # date = (datetime.now()+timedelta(days=day)).strftime("%Y%m%d")
    # dp_day = root_dp.joinpath('国补订单附件'+date)

    dp_day = pathlib.Path(dp)
    if not dp_day.is_dir():
        print(dp_day, 'not exist')
        return
    get_invoice_one_company_day(dp_day)
    return

# def get_invoice_all_store_one_day(day):
#     root_dp = pathlib.Path('E:/share/')
#     for dp in root_dp.iterdir():
#         if not dp.is_dir(): continue
#         date = (datetime.now()+timedelta(days=day)).strftime("%Y%m%d")
#         print(date)
#         dp_day = dp.joinpath('国补订单附件'+date)
#         get_invoice_one_store_day(dp_day)
#     return

def main():
    # root_dp = 'E:/share/HengTan/国补订单附件20260814'
    # root_dp = './imgs/hengtan/国补订单附件20260812/'
    # root_dp = './imgs/国补订单附件20260730/'
    # root_dp = './imgs/国补订单附件2026072210210/'
    # root_dp = './imgs/国补订单附件-rongyao/'
    # root_dp = './imgs/国补订单附件-qijian/'
    # root_dp = './imgs/国补订单附件-pinpai/'
    # root_dp = './imgs/国补订单附件-beiting/'
    # root_dp = './imgs/国补订单附件-pingguo/'
    # get_invoice_one_store_day(root_dp)

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--date_offset", type=int, help="offset day: 0 = today, -1 = yesterday, negative numbers for past days")
    # argcomplete.autocomplete(parser)  # enable tab complete hook
    # args = parser.parse_args()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    argcomplete.autocomplete(parser)  # enable tab complete hook
    args = parser.parse_args()

    get_invoice_all_store_one_day(args.dir)

    # print('accounting.py called at', datetime.now())
    return


if __name__ == '__main__':
    main()
