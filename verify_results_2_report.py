import json
import pathlib
import argparse
from utils.io import dump_list_txt, load_list_txt
from utils.filepath import find_jiuxun_fp
from jiuxun_info import get_jiuxun_info

def qrcode99_report(orders_dp):
    orders_dp = pathlib.Path(orders_dp)
    qrcode99_missing = json.load(open(orders_dp.joinpath('qrcode99_missing.json'), 'r', encoding='utf-8')) if orders_dp.joinpath('qrcode99_missing.json').is_file() else {}

    for dp in orders_dp.iterdir():
        if not dp.is_dir(): continue
        print('checking', dp)
        order_id = dp.name.split('（')[0]

        receipt = json.load(open(dp.joinpath('receipt.json'), 'r', encoding='utf-8')) if dp.joinpath('receipt.json').is_file() else {}
        jiuxun_fp = find_jiuxun_fp(dp)
        jiuxun = get_jiuxun_info(jiuxun_fp)

        if jiuxun['销方公司名称'] == '陕西恒檀通信有限公司':
            # print(receipt)
            if receipt['qrcode']['combined'] == '':
                '''check with receipt current 002026 code'''
                if receipt['qrcode'].get('code002026', '') != '' and receipt['qrcode'].get('code002026', '') == qrcode99_missing.get(order_id, '').split('+')[0]:
                    receipt['qrcode']['combined'] = qrcode99_missing.get(order_id)
                    # TODO check with receipt current 002026 code'''
                    json.dump(receipt, open(dp.joinpath('receipt.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
                else:
                    qrcode99_missing[order_id] = ''
    json.dump(qrcode99_missing, open(orders_dp.joinpath('qrcode99_missing.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

def gov_transfer(orders_dp):
    orders_dp = pathlib.Path(orders_dp)
    error_list = json.load(open(orders_dp.joinpath('error_list.json'), 'r', encoding='utf-8')) if orders_dp.joinpath('error_list.json').is_file() else {}
    report = []

    report.append(orders_dp.name[-8:]+' 国补检查')
    report.append('')
    for order_id, status in error_list.items():
        if status != 'check':
            report.append(str('订单号: '+order_id))
            if type(status) == dict:
                for type_, error_ in status.items():
                    report.append(str(type_+': '+error_).replace('!=', '不等于').replace('seller: ', '销售人: '))
            else:
                report.append(str(status))
            report.append('')
    report.append('尽快检查国补资料 核实后 私信我')
    dump_list_txt(report, orders_dp.joinpath('report.txt'))
    # json.dump(error_list, open(orders_dp.joinpath('report.txt'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
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
    args = parser.parse_args()

    qrcode99_report(args.dir)
    # gov_transfer(args.dir)

    # print('verify.py called at', datetime.now())
    return


if __name__ == '__main__':
    main()