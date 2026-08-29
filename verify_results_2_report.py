import json
import pathlib
import argparse

def transfer(orders_dp):
    orders_dp = pathlib.Path(orders_dp)
    error_list = json.load(open(orders_dp.joinpath('error_list.json'), 'r', encoding='utf-8')) if orders_dp.joinpath('error_list.json').is_file() else {}
    report = []

    for order_id, status in error_list.items():
        if status != 'check':
            print(str('订单号: '+ order_id))
            for type_, error_ in status.items():
                print(str(type_+': '+error_).replace('!=', '不等于'))

    json.dump(error_list, open(orders_dp.joinpath('report.txt'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
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

    transfer(args.dir)

    # print('verify.py called at', datetime.now())
    return


if __name__ == '__main__':
    main()