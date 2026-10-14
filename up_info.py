import argparse
import json
import pathlib
import traceback
import urllib.request
from PIL import Image, ImageDraw, ImageEnhance
from invoice import get_invoice_url, extract_invoice
from jiuxun_info import get_jiuxun_info, get_gov_subsidy_order_detail, get_jiuxun_json
from utils.filepath import find_invoice_fp, find_jiuxun_fp, find_id_fp, find_phone_fp, find_receipt_fp, find_conf_fp, find_combined_fp
from utils.pdf import pdf2img
from utils.geometry import resize_for_doubao
from store import load_store_config
from verify_results_2_report import qrcode99_report

jiuxun_type_2_up_type = {
    '智能手机': '手机',
    '平板电脑': '平板',
    '智能手表': '智能手表手环',
    '智能手环': '智能手表手环',
    '智能眼镜': '智能眼镜',
}

def verify_jiuxun_invoice(jiuxun, invoice):
    inconsistency = {}

    return jiuxun, invoice

def get_default_info():
    uploading_info = {
        '包含完整外包装及sn码的激活照片': '验机激活四码合一照片.jpg',
        '商品SN码': '',
        'imei1': '',
        'imei2': '',
        '品类': '',
        '签购单': '销售小票及刷卡小票.jpg',
        '发票类型': '数电普票',
        '发票': 'invoice.jpg',
        '补贴确认书': '3C购新补贴确认书.jpg',
        '外部订单号': '',
        '发票号码': '',
        '开票日期': '',
        '商户号': '',
        '购买数量': '1',
        '发票金额': '',
        '发票税额': '',
        '销售方纳税人识别号': '',
        '企业名称': '',
        '消费者姓名': '',
        '收货省市区': '',
        '系统参考号': '',
        '是否自提': '自提',
        '是否交旧': '否',
        '签收时间': '',
        '终端号': '',
        '交易日期': '',
        '交易类型': '二维码交易',
        '收货人姓名': '',
    }
    return uploading_info


def get_up_info(orders_dp):
    # size = 1670208 # ~0.14MB
    size = 26702080 # ~0.14MB

    orders_dp = pathlib.Path(orders_dp)
    print(orders_dp.is_dir())
    if not orders_dp.is_dir():
        print(orders_dp, 'not exist')
        return
    print('building', orders_dp)

    # uploading_info_day = {}

    error_list = json.load(open(orders_dp.joinpath('error_list.json'), 'r', encoding='utf-8')) if orders_dp.joinpath('error_list.json').is_file() else {}
    jiuxun_file_json = get_jiuxun_json(orders_dp.joinpath('filelist.json'))
    # invoice_urls = get_invoice_url(jiuxun_file_json)
    # invoice_urls = get_invoice_url(orders_dp.joinpath('国补订单明细.xlsx'))
    # print(invoice_urls)
    qrcode99_report(orders_dp)

    store = load_store_config()
    invoice_inputs_per_company = {}
    invoice_unputs_per_company = {}

    for order_dp in orders_dp.iterdir():
        order_id = order_dp.name.split('（')[0]
        if not order_dp.is_dir() or error_list.get(order_id, None) != 'check':
            print(order_dp, 'uncheck')
            continue
        try:
            '''get jiuxun info'''
            jiuxun_fp = find_jiuxun_fp(order_dp)
            jiuxun = get_jiuxun_info(jiuxun_fp)
            file_json = jiuxun_file_json[order_id]
            if jiuxun['销方公司名称'] != '陕西恒檀通信有限公司':
                continue
            if jiuxun_type_2_up_type.get(jiuxun['分类'], '品类错误') == '品类错误':
                print('ignore', order_id, 'type is', jiuxun['分类'])
                continue
            print('building', order_dp)
            urllib.request.urlretrieve(file_json['3C购新补贴确认书.jpg'], order_dp.joinpath('3C购新补贴确认书.jpg'))
            urllib.request.urlretrieve(file_json[find_combined_fp(order_dp).name], order_dp.joinpath('验机激活四码合一照片.jpg'))

            resize_for_doubao(Image.open(find_combined_fp(order_dp)), size).save(order_dp.joinpath('验机激活四码合一照片.jpg'))
            resize_for_doubao(Image.open(order_dp.joinpath('销售小票及刷卡小票.jpg')), size).save(order_dp.joinpath('销售小票及刷卡小票.jpg'))
            resize_for_doubao(Image.open(find_conf_fp(order_dp)), size).save(find_conf_fp(order_dp))

            receipt = json.load(open(order_dp.joinpath('receipt.json'), 'r', encoding='utf-8'))
            receipt_qr_info = receipt['qrcode']['combined'].split('+')

            invoice_url = file_json['发票.pdf']
            urllib.request.urlretrieve(file_json['发票.pdf'], order_dp.joinpath('发票.pdf'))

            # invoice_url = invoice_urls.get(order_id, None)

            if not invoice_url:
                if invoice_unputs_per_company.get(jiuxun['销方公司名称'], None):
                    invoice_unputs_per_company[jiuxun['销方公司名称']].update({jiuxun['订单号']: {}})
                else:
                    invoice_unputs_per_company[jiuxun['销方公司名称']] = {jiuxun['订单号']: {}}
                continue
            inv, txt, full_text = extract_invoice(invoice_url)
            json.dump(inv, open(order_dp.joinpath('inv.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

            pdf2img(invoice_url, order_dp.joinpath('invoice.jpg'))
            # print(json.dumps(inv, indent=2, ensure_ascii=False))

            uploading_info = get_default_info()
            uploading_info['包含完整外包装及sn码的激活照片'] = str(order_dp.joinpath('验机激活四码合一照片.jpg'))
            uploading_info['商品SN码'] = jiuxun['SN']
            uploading_info['imei1'] = jiuxun['序列号'] if jiuxun['分类']=='智能手机' or jiuxun['分类']=='智能手机' else ''
            uploading_info['imei2'] = jiuxun['序列号2'] if jiuxun['分类']=='智能手机' else ''
            uploading_info['品类'] = jiuxun_type_2_up_type.get(jiuxun['分类'], '品类错误')
            uploading_info['签购单'] = str(order_dp.joinpath('销售小票及刷卡小票.jpg'))
            uploading_info['发票'] = str(order_dp.joinpath('invoice.jpg'))
            uploading_info['补贴确认书'] = str(order_dp.joinpath('3C购新补贴确认书.jpg'))
            uploading_info['外部订单号'] = receipt_qr_info[0]
            uploading_info['商户订单号'] = receipt_qr_info[5]
            uploading_info['发票号码'] = inv['invoice_number']
            uploading_info['开票日期'] = inv['invoice_date']
            uploading_info['商户号'] = receipt_qr_info[1]
            uploading_info['发票金额'] = inv['total_amount'] if float(inv['total_amount']) == float(jiuxun['国补收银金额'])+float(jiuxun['补贴金额']) else '计算错误'
            print('发票金额', inv['total_amount'])
            print('国补收银金额', float(jiuxun['国补收银金额']))
            print('补贴金额', float(jiuxun['补贴金额']))
            print(float(jiuxun['国补收银金额'])+float(jiuxun['补贴金额']))
            uploading_info['发票税额'] = inv['tax'] if float(inv['tax']) == round(float(float(jiuxun['国补收银金额'])+float(jiuxun['补贴金额']))/(1+store[jiuxun['销方公司名称']]['tax_rate'])*store[jiuxun['销方公司名称']]['tax_rate'], 2) else '计算错误'
            uploading_info['销售方纳税人识别号'] = inv['seller_id']
            uploading_info['企业名称'] = jiuxun['销方公司名称']
            uploading_info['消费者姓名'] = jiuxun['联系人']
            uploading_info['收货省市区'] = store[jiuxun['销方公司名称']]['area']
            uploading_info['系统参考号'] = receipt_qr_info[4]
            uploading_info['签收时间'] = receipt_qr_info[3]
            uploading_info['终端号'] = receipt_qr_info[2]
            uploading_info['交易日期'] = receipt_qr_info[3]
            uploading_info['收货人姓名'] = jiuxun['联系人']

            json.dump(uploading_info, open(order_dp.joinpath('uploading_up.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

            if invoice_inputs_per_company.get(jiuxun['销方公司名称'], None):
                invoice_inputs_per_company[jiuxun['销方公司名称']].update({jiuxun['订单号']: uploading_info})
            else:
                invoice_inputs_per_company[jiuxun['销方公司名称']] = {jiuxun['订单号']: uploading_info}

            print(invoice_inputs_per_company)
        except Exception as e:
            print(order_id, ' checking error:', e)
            traceback.print_exc()

            # traceback.print_exc()
            json.dump(error_list, open(orders_dp.joinpath('error_list.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    for company, invoice_inputs in invoice_inputs_per_company.items():
        json.dump(invoice_inputs, open(orders_dp.joinpath('UP_uploading_'+company+'.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    for company, invoice_unputs in invoice_unputs_per_company.items():
        json.dump(invoice_unputs, open(orders_dp.joinpath('UP_unloading_'+company+'.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    args = parser.parse_args()

    get_up_info(args.dir)
    return


if __name__ == '__main__':
    main()
