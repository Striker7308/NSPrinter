import argparse
import argcomplete
import pandas as pd
import pathlib
from datetime import datetime, timedelta
import json

def report_to_done_order(dp_day):
    dp_day = pathlib.Path(dp_day)
    seller2wecom_id = json.load(open('./config/seller2wecomID.json', 'r', encoding='utf-8'))

    today_16 = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    today_2050 = datetime.now().replace(hour=20, minute=50, second=0, microsecond=0)
    # date = (datetime.now()).strftime("%Y%m%d")

    dp_xlsx = dp_day.joinpath('订单列表.xlsx')
    to_done_xlsx = pd.read_excel(dp_xlsx)
    # print(to_done_xlsx)
    print(to_done_xlsx.columns)
    subset = to_done_xlsx.iloc[:, [0, 1, 9, 10]]
    # print(subset)

    output = ''
    print(dp_day.name[-8:], '挂单检查')
    print(str(subset.columns.tolist()).replace('\'', '').replace(',', ' ').replace('[', '').replace(']', '').replace('代码', ''))

    # title
    output += dp_day.name[-8:]+' 挂单检查' + '\n'
    # column meaning
    output += str(subset.columns.tolist()).replace('\'', '').replace(',', ' ').replace('[', '').replace(']', '').replace('代码', '')+'\n'

    # each order
    for row in subset.itertuples(index=False, name=None):
        store, order_num, order_time, seller = row
        order_time = datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < today_2050 and order_time > today_16:
            continue
        # print(order_time)
        # print(type(order_time))
        output += str(store)+' '+str(order_num)+' '+str(order_time.strftime("%H:%M"))+' '+str(seller2wecom_id.get(seller, seller))+'\n'
        print(store, order_num, order_time.strftime("%H:%M") , seller2wecom_id.get(seller, seller))
    output += '尽快完成 方便开票'+'\n'
    print('尽快完成 方便开票')

    with open(dp_day.joinpath('leftover.txt'), "w", encoding="utf‑8") as f:
        f.write(output)
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    argcomplete.autocomplete(parser)  # enable tab complete hook
    args = parser.parse_args()

    report_to_done_order(args.dir)
    return

if __name__ == '__main__':
    main()
