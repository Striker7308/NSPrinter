import pandas as pd
import json
import pathlib
from datetime import datetime, timedelta


def str2list(raw_str):
    # split by \r\n, strip each entry, drop empty strings
    parts = [p.strip() for p in str(raw_str).split('\r\n')]
    return [p for p in parts if p]


def get_gov_subsidy_order_detail(dp_day):
    dp_day = pathlib.Path(dp_day)
    dp_xlsx = dp_day.joinpath('国补订单明细.xlsx')
    gov_subsidy_xlsx = pd.read_excel(dp_xlsx, dtype=str)
    gov_subsidy_order = gov_subsidy_xlsx.set_index("订单号").to_dict(orient="index")

    print(gov_subsidy_order['合计'])
    print(gov_subsidy_order['合计']['订单附件下载链接'])
    if gov_subsidy_order.get('合计', None): gov_subsidy_order.pop('合计')

    # Convert the multi-line url string into list
    for detail in gov_subsidy_order.values():
        detail["订单附件下载链接"] = str2list(detail["订单附件下载链接"])

    json.dump(gov_subsidy_order, open(dp_day.joinpath('gov_subsidy_detail.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    gov_subsidy_order = json.load(open(dp_day.joinpath('gov_subsidy_detail.json'), 'r', encoding='utf-8')) if dp_day.joinpath('gov_subsidy_detail.json').is_file() else {}
    print(gov_subsidy_order)

    return gov_subsidy_order


def main():
    dp = 'E:/share/国补订单附件20260926/'
    od = get_gov_subsidy_order_detail(dp)
    print(od)
    print(od.keys())
    return

if __name__ == "__main__":
    main()
