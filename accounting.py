import json
import pathlib
import time

from utils.filepath import find_invoice_fp, find_jiuxun_fp

from id import get_id
from receipt import get_receipt, get_signature
from sn import get_sn
from invoice import get_invoice
from jiuxun_info import get_jiuxun_info, get_product_detail
from store import load_store_config

def main():
    # root_dp = './imgs/国补订单附件20260730/'
    # root_dp = './imgs/国补订单附件2026072210210/'
    # root_dp = './imgs/国补订单附件-rongyao/'
    # root_dp = './imgs/国补订单附件-qijian/'
    root_dp = './imgs/国补订单附件-pinpai/'
    # root_dp = './imgs/国补订单附件-beiting/'
    # root_dp = './imgs/国补订单附件-pingguo/'
    root_dp = pathlib.Path(root_dp)
    store = load_store_config()

    status_list = {}

    for dp in root_dp.iterdir():
        if not dp.is_dir(): continue
        status = 1
        # dp = './imgs/国补订单附件2026072119282/10221431（未审核）/'
        # dp = './imgs/10219792（未审核）'
        # dp = './imgs/国补订单附件2026072210210/10224861（未审核）/'
        # dp = './imgs/国补订单附件-pingguo/10221921（未审核）/'
        # print(str(dp))

        id, phone, receipt, invoice, jiuxun = get_det(dp)
        order_id = {
            'order_id': jiuxun['订单号'],
            'seller': jiuxun['销售人'],
        }

        check = check_store_info(store, receipt, jiuxun)
        check = {**check, **check_customer_info(id, receipt, jiuxun)}
        # check_payment(receipt, jiuxun)
        check = {**check, **check_merchandise_info(phone, receipt, jiuxun)}

        json.dump({**order_id, **check}, open(str(dp)+'/check.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

        for key, checked in check.items():
            if not checked == True:
                for key_error, check_error in check.items():
                    if not check_error == True:
                        print(key_error, check_error)
                        status = 0
                break


        local_time = time.localtime(time.time())
        local_time_str = time.strftime("%Y%m%d", local_time)
        print(dp, 'current time:', local_time_str)  # date string: 2026‑08‑12

        json.dump(status, open(str(dp)+'/status.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

        with open(str(dp)+'/status.json', 'r', encoding='utf-8') as f:
            status = json.load(f)
        print(dp, 'status', status)

        status_list[order_id['order_id']] = status
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

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
    json.dump(status_list, open(str(root_dp) + '/status.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return


if __name__ == '__main__':
    main()