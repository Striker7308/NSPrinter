import argparse
import argcomplete
import pandas as pd
import pathlib
from datetime import datetime, timedelta
import json

def report_to_done_order(fp):
    # seller2wecom_id = json.load(open('./config/seller2wecomID.json', 'r', encoding='utf-8'))
    feb = datetime(2026, 2, 15)

    dp_xlsx = pathlib.Path(fp)
    to_done_xlsx = pd.read_excel(dp_xlsx)
    # print(to_done_xlsx)

    for i, ele in enumerate(to_done_xlsx.columns):
        print(i, ele)
    print(to_done_xlsx.columns)
    # subset = to_done_xlsx.iloc[:, [3, 5, 10, 13, 24, 26, 27]]
    subset = to_done_xlsx.iloc[:, [3, 4, 5, 6, 7, 9, 10, 13, 14, 18, 19, 24, 25, 26, 27]]
    print(subset.columns)

    print('all customer len', len(subset))
    subset['最后消费时间'] = pd.to_datetime(subset['最后消费时间'], errors='coerce')
    df_filtered = subset.loc[subset['最后消费时间'] < feb, :]
    print('all customer len before', feb, len(df_filtered))

    print(fp, '会员')
    for i, row in enumerate(df_filtered.itertuples(index=False, name=None)):
        # row is tuple: (col0_value, col1_value, col10_value)
        print(row)
        if i > 100: break
    print(len(df_filtered))
    df_filtered.to_excel(dp_xlsx.parent.joinpath('apple_customer.xlsx'), index=False)

    return

def main():
    report_to_done_order('./imgs/apple_customer_all.xlsx')
    return

if __name__ == '__main__':
    main()
