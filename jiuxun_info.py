import pandas as pd
import json
import pathlib

def str2list(raw_str):
    # split by \r\n, strip each entry, drop empty strings
    parts = [p.strip() for p in str(raw_str).split('\r\n')]
    return [p for p in parts if p]

def get_product_detail(jiuxun):
    # 商品名称：一加 Turbo 6（PLU110）全网通5G版 金币版
    # 规格：追光银 16GB+512GB
    # 分类：智能手机
    # 品牌：一加（OnePlus）
    product = jiuxun['商品名称'].split('（')[0]+jiuxun['规格'].split('[')[0]
    return product.replace(' ', '')

def get_jiuxun_info(fp='./imgs/国补订单附件-pinpai/10224732（未审核）/10224732订单信息.txt'):
    flag_debug = False
    jiuxun = {}
    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            k, v = line.split("：", 1)
            jiuxun[k.strip()] = v.strip()
            if k.strip() == '发票备注':
                v = v.strip()
                i_start = v.find('购买方地址')
                i_end = v.find('，', i_start)
                jiuxun['customer_address'] = v[i_start+6:i_end]
        f.close()
    if flag_debug: print(json.dumps(jiuxun, indent=2, ensure_ascii=False))
    return jiuxun


def get_gov_subsidy_order_detail(dp_day):
    dp_day = pathlib.Path(dp_day)
    dp_xlsx = dp_day.joinpath('国补订单明细.xlsx')
    gov_subsidy_xlsx = pd.read_excel(dp_xlsx, dtype=str)

    '''convert to json using order id'''
    gov_subsidy_order = gov_subsidy_xlsx.set_index("订单号").to_dict(orient="index")
    if gov_subsidy_order.get('合计', None): gov_subsidy_order.pop('合计')   # get rid of last '合计' line

    # Convert the multi-line url string into list
    for detail in gov_subsidy_order.values():
        detail["订单附件下载链接"] = str2list(detail["订单附件下载链接"])

    '''save as json'''
    json.dump(gov_subsidy_order, open(dp_day.joinpath('gov_subsidy_detail.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    return gov_subsidy_order


def main():
    get_jiuxun_info()

if __name__ == '__main__':
    main()