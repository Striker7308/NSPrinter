import argparse
import json
from datetime import datetime
from operator import index

import pandas as pd
import pathlib

def excel_to_json(excel, keyword='订单号'):
    excel = excel.reset_index()
    excel = excel.loc[:, ['订单号', '销售', '商品SN', '加单时间', '合同号']]
    excel = excel.set_index(keyword)
    json_ = excel.T.to_dict()
    return json_

def json_to_wecom(json_, keyword='九讯云订单号'):
    out = ''
    for id_, val in json_.items():
        out += keyword+': '+id_+'\n'
        for key, val_ in val.items():
            out += key+': '+val_+'\n'
        out += '>>>>>>>>>>>>>>>>>>>>>>>>\n'
    return out

def excel_2_wecom(excel, keyword='九讯云订单号'):
    json_ = excel_to_json(excel)
    return json_to_wecom(json_, keyword)

def output_up_json(audit_ids, up_orders):
    up_json_keys = ('goodsSn', 'dealTime', 'updTs', 'uploadUserName', 'saleName', 'goodsId')
    out_keys = ('SN', '交易时间', '上传时间', '上传人', '销方公司', '商品名称')
    up_orders_filtered = {}
    for audit_id in audit_ids:
        if audit_id in up_orders:
            up_order = {}
            for key_, key in zip(out_keys, up_json_keys):
                up_order[key_] = up_orders[audit_id][key]
            up_orders_filtered[audit_id] = up_order
    return up_orders_filtered

def check_repeat_audit_id(yun_xlsx):
    order_audit_id = yun_xlsx.set_index("合同号")
    is_audit_dup = order_audit_id.index.duplicated(keep=False)
    dup_rows = order_audit_id[is_audit_dup]
    dup_rows = dup_rows.loc[:, ['订单号', '销售', '商品SN', '加单时间']]
    print('num yun ', len(order_audit_id))
    # print(dup_rows.to_string(index=False, show_dimensions=False))
    # print('-------------------------')

    print('外部订单号重复 '+str(len(dup_rows))+'个 开始\n')
    print(excel_2_wecom(dup_rows))
    print('外部订单号重复 结束')

    yun_audit_id_unique_xlsx = order_audit_id[~is_audit_dup]
    print('num yun unq ',len(yun_audit_id_unique_xlsx))

    dup_rows = dup_rows.reset_index()
    yun_audit_id_unique_xlsx = yun_audit_id_unique_xlsx.reset_index()
    return yun_audit_id_unique_xlsx, dup_rows

def check_audit_id_num(yun_xlsx):
    order_audit_id = yun_xlsx.set_index("合同号")
    audit_id = order_audit_id.index.tolist()
    iss25 = [True if type(audit_id) == str and len(audit_id) == 25 else False for audit_id in audit_id]
    iss_25dig = [True if type(audit_id) == str and iss25 and audit_id.isdigit() else False for is25, audit_id in zip(iss25, audit_id)]
    isnts_25dig = [not is_25dig for is_25dig in iss_25dig]
    # audit_id_not25 = [audit_id for audit_id in audit_id if type(audit_id) == str and len(audit_id) != 25]
    # audit_id_25 = [audit_id for audit_id in audit_id if type(audit_id) == str and len(audit_id) == 25]
    order_audit_id_not25 = order_audit_id.loc[isnts_25dig, ['订单号', '销售', '商品SN', '加单时间']]
    # order_audit_id_not25 = order_audit_id.loc[audit_id_not25, ['订单号', '销售', '商品SN', '加单时间']]

    print('num yun audid', len(audit_id))
    # print('num yun not25', len(audit_id_not25))
    # print('num yun exa25', len(audit_id_25))

    order_audit_id_25dig = order_audit_id.loc[iss_25dig, ['订单号', '销售', '商品SN', '加单时间']]
    # order_audit_id_25 = order_audit_id.loc[audit_id_25, ['订单号', '销售', '商品SN', '加单时间']]
    order_audit_id_not25 = order_audit_id_not25.reset_index()
    order_audit_id_not25 = order_audit_id_not25.set_index('订单号')

    print('外部订单号位数错误 '+str(len(order_audit_id_not25))+'个 开始\n')
    print()
    # print(excel_2_wecom(order_audit_id_not25))
    print('外部订单号位数错误 结束\n')

    # print('-------------------------')
    # for order_id in order_audit_id_not25.index:
    #     print('九讯云订单号 ', order_id)
    #     for key, val in order_audit_id_not25.loc[order_id].items():
    #         print(key, val) if key != '合同号' else print('外部订单号', val, '位数', len(val))
    #     print('-------------------------')

    order_audit_id_not25 = order_audit_id_not25.reset_index()
    order_audit_id_25dig = order_audit_id_25dig.reset_index()
    return order_audit_id_25dig, order_audit_id_not25

def check_missing_union_pay(yun_order_25, up_order):
    json_keys = list(up_order.keys())
    print('num up ord', json_keys[0])
    # yun_order_25['exists_in_json'] = yun_order_25['外部订单号'].isin(json_keys)

    is_up = yun_order_25['合同号'].isin(json_keys)
    print('num exists', len(is_up))
    print('num exists', is_up[0])
    # not_exists_in_json = [False for exist in exists_in_json if exist else True]

    yun_order_match = yun_order_25[is_up]
    yun_order_missing = yun_order_25[~is_up]

    print('num yun match', len(yun_order_match))
    print('num up ', len(up_order))
    '''get up order not in 9yun'''
    up_audit_id_missing = [audit_id for audit_id in up_order.keys() if audit_id not in set(yun_order_match['合同号'].tolist())]
    t = datetime(2026,9,1)
    up_audit_id_missing_ = [audit_id for audit_id in up_audit_id_missing if datetime.strptime(up_order[audit_id]['dealTime'], '%Y-%m-%d %H:%M:%S') > t]
    up_audit_id_missing = up_audit_id_missing_

    '''get up order rejected'''
    up_audit_id_rejected = [audit_id for audit_id in up_order.keys() if up_order[audit_id]['auditRoleNm']=='2026年陕西数码市级线下复审' and up_order[audit_id]['auditInfo']!='通过']
    print('num up_ reject', len(up_audit_id_rejected))

    '''get up order out of time'''
    yun_order_json = excel_to_json(yun_order_25, '合同号')

    t = datetime(2026,10,10)
    up_audit_id_oot = [audit_id for audit_id in up_order.keys() if (up_order[audit_id]['auditRoleNm'] == '' or up_order[audit_id]['auditRoleNm'] == '2026年陕西数码市级线下初审') and len(up_order[audit_id]['dealTime']) and datetime.strptime(up_order[audit_id]['dealTime'], '%Y-%m-%d %H:%M:%S') < t]
    up_audit_id_oot_per_company = {'陕西恒檀通信有限公司':{}, '陕西恒国通信有限公司':{}, '商洛市商州区宁致远通讯部':{}, '南洛市商州区宁致远通讯部':{}}
    for audit_id in up_audit_id_oot:
        order_oot = {audit_id: {'订单号': yun_order_json.get(audit_id, {}).get('订单号', 'no yunid'),
                                '交易时间': up_order[audit_id]['dealTime'],
                                '审核': up_order[audit_id]['auditRoleNm']}}
        sale_comp = up_order[audit_id]['saleName']
        # order_oot = {yun_order_json.get(audit_id, {}).get('订单号', 'no yunid'), audit_id, up_order[audit_id]['dealTime'], up_order[audit_id]['auditRoleNm'], up_order[audit_id]['saleName']}
        # print(yun_order_json.get(audit_id, {}).get('订单号', 'no yunid'), audit_id, up_order[audit_id]['dealTime'], up_order[audit_id]['auditRoleNm'], up_order[audit_id]['saleName'])
        if up_audit_id_oot_per_company.get(sale_comp, False):
            up_audit_id_oot_per_company[sale_comp].update(order_oot)
        else:
            up_audit_id_oot_per_company[sale_comp]=order_oot
        # up_audit_id_oot_per_company[sale_comp] = up_audit_id_oot_per_company[sale_comp].update(order_oot) if up_audit_id_oot_per_company.get(sale_comp, False) else order_oot
        # up_audit_id_oot_per_company[up_order[audit_id]['saleName']].update(order_oot)
    print('num up_ OOT', len(up_audit_id_oot))
    for comp, de in up_audit_id_oot_per_company.items(): print(comp, ' has ', len(de))
    print(json.dumps(up_audit_id_oot_per_company, indent=2, ensure_ascii=False))

    # print(up_audit_id_oot_per_company)
    # 0020260914103748002661803
    # print(up_order)
    # print('num up_ unmatch', len(up_audit_id_missing))
    # print('num up_ unmatch', len(up_order)-len(yun_order_match))
    # print(up_audit_id_missing[0])
    # print(up_audit_id_missing[-1])
    # print('num yun_ma', len(yun_order_match.index))
    # print('num yun_un', len(yun_order_missing.index))
    # print('num yun', len(yun_order_missing.index)+len(yun_order_match.index))

    print('num up_ord', len(json_keys))

    yun_order_missing = yun_order_missing.loc[:, ['订单号', '销售', '商品SN', '加单时间', '合同号']]
    yun_order_json_missing = excel_to_json(yun_order_missing)
    t = datetime(2026,10,20)
    yun_order_json_missing_ = {k: v for k, v in yun_order_json_missing.items() if datetime.strptime(v['加单时间'], '%Y-%m-%d %H:%M:%S') < t}
    yun_order_json_missing = yun_order_json_missing_

    print('未上传银联 '+str(len(yun_order_json_missing))+'个 开始\n')
    # print(json_to_wecom(yun_order_json_missing))
    # print(yun_order_missing.to_string(index=False, show_dimensions=False))
    print('未上传银联 结束\n')

    print('未录入9讯云 '+str(len(up_audit_id_missing))+'个 开始\n')
    up_audit_id_missing = output_up_json(up_audit_id_missing, up_order)
    # print(json_to_wecom(up_audit_id_missing, '外部订单号'))
    print('未录入9讯云 结束\n')

    print('提交银联失败 开始\n')
    print('提交银联失败 结束\n')

    return

def read_9yun_gov_sub_order_excel(fp='E:/share/unionpay_revise/国补订单明细.xlsx'):
    up_dp = pathlib.Path('E:/share/unionpay_revise/')
    # dp_xlsx = dp_day.joinpath('国补订单明细.xlsx')
    yun_xlsx = pd.read_excel(pathlib.Path(fp), dtype=str,skipfooter=1)
    up_orders = json.load(open(up_dp.joinpath('unionpay_恒檀_20260901_20261023.json'), 'r', encoding='utf-8')) if up_dp.joinpath('unionpay_恒檀_20260901_20261023.json').is_file() else {}
    up_orders_ = json.load(open(up_dp.joinpath('unionpay_恒国_20260901_20261025.json'), 'r', encoding='utf-8')) if up_dp.joinpath('unionpay_恒国_20260901_20261025.json').is_file() else {}
    up_orders.update(up_orders_)
    up_orders_ = json.load(open(up_dp.joinpath('unionpay_宁致远_20260901_20261025.json'), 'r', encoding='utf-8')) if up_dp.joinpath('unionpay_宁致远_20260901_20261025.json').is_file() else {}
    up_orders.update(up_orders_)
    print('num up_orders', len(up_orders))

    yun_audit_id_unique_xlsx, _ = check_repeat_audit_id(yun_xlsx)
    yun_order_audit_id_25, _ = check_audit_id_num(yun_audit_id_unique_xlsx)

    check_missing_union_pay(yun_order_audit_id_25, up_orders)

    # gov_subsidy_order_audit_id = gov_subsidy_9yun_xlsx.set_index("合同号")
    # gov_subsidy_order_audit_id.to_string()
    # print(gov_subsidy_order_audit_id.columns)
    # # print('9yun 合同号不重复？：', gov_subsidy_order_audit_id.index.is_unique())
    # gov_subsidy_order_audit_id["is_dup"] = gov_subsidy_order_audit_id.index.duplicated(keep=False)
    # dup_rows = gov_subsidy_order_audit_id[gov_subsidy_order_audit_id["is_dup"]]
    # dup_rows = dup_rows.loc[:, ['订单号','销售','商品SN','加单时间']]
    # dup_rows = dup_rows.reset_index()
    # print(dup_rows.to_string(index=False, show_dimensions=False))
    # # print(dup_rows.to_string())

    gov_subsidy_order_yun_id = yun_xlsx.set_index("订单号").to_dict(orient="index")

    # gov_subsidy_order_audit_id
    #
    # for key, val in gov_subsidy_order_yun_id.items():
    #     print(key)
    #     for key_, val_ in val.items():
    #         aduit_id_2_9yun_id[key_] = aduit_id_2_9yun_id.get(key_, []) + [val_]
    #         print(key_)
    #         print(val_)
    #     break
    #         # print(key_, len(key_))
    #     #     print(len(key_), len(val_))
    #     #     break
    # # gov_subsidy_order - gov_subsidy_order.to_dict(orient="index")
    # # print(freq_aduit_id)
    # for aduit_id, yun_ids in aduit_id_2_9yun_id.items():
    #     if len(yun_ids) > 1:
    #         print('外部订单号重复：', aduit_id)
    #         for yun_id in yun_ids:
    #             print('九讯云订单号：', yun_id)
    #             order = gov_subsidy_order_yun_id[yun_id]
    #             print('销售', gov_subsidy_order_yun_id[yun_id]['销售'])
    #             print('状态', gov_subsidy_order_yun_id[yun_id]['订单状态'])
    #         print('外部订单号：', aduit_id)
    #         print('>>>>>>>>>>>>>>>>>>>>>>>>')

    # gov_subsidy_order = gov_subsidy_xlsx.set_index("订单号").to_dict(orient="index")
    # print(gov_subsidy_order)
    return

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    # args = parser.parse_args()
    # read_9yun_gov_sub_order_excel(args.dir)
    read_9yun_gov_sub_order_excel()

    return

if __name__ == '__main__':
    main()