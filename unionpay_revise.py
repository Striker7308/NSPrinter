import argparse
import json
from datetime import datetime, timedelta
from http.cookiejar import debug
from operator import index
import pandas as pd
import pathlib


def simplify_name(company_name):
    return company_name.replace('陕西', '').replace('商洛市', '').replace('商州区', '').replace('通信', '').replace('有限公司', '').replace('通讯', '').replace('部', '')

def simplify_up_excel(up_orders, yun_order):
    yun_order_json = excel_to_json(yun_order, '合同号')

    yun_id_rejected = [yun_order_json.get(audit_id, {}).get('订单号', 'notFound') for audit_id in up_orders.loc[:,'auditOrderId']]
    seller_rejected = [yun_order_json.get(audit_id, {}).get('销售', 'notFod') for audit_id in up_orders.loc[:,'auditOrderId']]
    up_orders = up_orders.loc[:, ['goodsSn', 'crtTs', 'auditOrderId', 'saleName', 'auditRoleNm', 'auditInfo', 'goodsId']]
    up_orders = up_orders.rename(columns={
        'goodsSn':'SN', 'crtTs':'上传时间', 'auditOrderId':'外部订单号','saleName':'商家', 'auditRoleNm':'审核段',
        'auditInfo':'审核态', 'goodsId':'商品'
    })
    up_orders.insert(0, "订单号", yun_id_rejected)
    up_orders.insert(1, "销售", seller_rejected)
    return up_orders

def simplify_up_record_excel(up_record_excel):
    up_record_excel = up_record_excel.reset_index()
    up_record_excel = up_record_excel.loc[:, ['交易时间', '银商订单号', '交易金额']]
    # yun_excel = yun_excel.loc[:, ['订单号', '销售', '商品SN', '加单时间', '合同号']]
    return up_record_excel

def simplify_yun_excel(yun_excel):
    yun_excel = yun_excel.reset_index()
    yun_excel = yun_excel.loc[:, ['订单号', '销售', '加单时间', '合同号']]
    # yun_excel = yun_excel.loc[:, ['订单号', '销售', '商品SN', '加单时间', '合同号']]
    return yun_excel

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

# def output_up_json(audit_ids, up_orders):
#     up_json_keys = ('goodsSn', 'dealTime', 'updTs', 'uploadUserName', 'saleName', 'goodsId')
#     out_keys = ('SN', '交易时间', '上传时间', '上传人', '销方公司', '商品名称')
#     up_orders_filtered = {}
#     for audit_id in audit_ids:
#         if audit_id in up_orders:
#             up_order = {}
#             for key_, key in zip(out_keys, up_json_keys):
#                 up_order[key_] = up_orders[audit_id][key]
#             up_orders_filtered[audit_id] = up_order
#     return up_orders_filtered

def check_repeat_audit_id(yun_xlsx):
    order_audit_id = yun_xlsx.set_index("合同号")
    is_audit_dup = order_audit_id.index.duplicated(keep=False)
    dup_rows = order_audit_id[is_audit_dup]
    dup_rows = dup_rows.loc[:, ['订单号', '销售', '商品SN', '加单时间']]
    print('外部订单号重复 '+str(len(dup_rows))+'个 开始\n')
    print(dup_rows.to_string(index=False, show_dimensions=False))
    # dup_rows.to_excel(writer, sheet_name='九讯云外部订单号重复')
    print('外部订单号重复 结束')

    # dup_rows = dup_rows.reset_index()
    yun_audit_id_unique_xlsx = order_audit_id[~is_audit_dup]
    yun_audit_id_unique_xlsx = yun_audit_id_unique_xlsx.reset_index()
    return yun_audit_id_unique_xlsx, dup_rows

def check_audit_id_num(yun_xlsx):
    iss_25dig = [True if type(audit_id) == str and len(audit_id) == 25 and audit_id.isdigit() else False for audit_id in yun_xlsx.loc[:, '合同号']]
    not_25dig = [not is_25dig for is_25dig in iss_25dig]
    order_audit_id_25dig = yun_xlsx.loc[iss_25dig, :]
    order_audit_id_not25 = yun_xlsx.loc[not_25dig, :]
    order_audit_id_not25_simp = simplify_yun_excel(order_audit_id_not25)
    print('外部订单号位数错误 '+str(len(order_audit_id_not25_simp))+'个 开始')
    print(order_audit_id_not25_simp.to_string(index=False, show_dimensions=False))
    # order_audit_id_not25_simp.to_excel(writer, sheet_name='外部订单号错位')
    print('外部订单号位数错误 结束\n')
    return order_audit_id_25dig, order_audit_id_not25_simp

def check_unload_union_pay(up_record_xlsx, up_xlsx, flag_debug=True):
    if flag_debug: print('num unionpay record ', len(up_record_xlsx), 'num up ', len(up_xlsx))
    # up_xlsx['updTs'] = pd.to_datetime(up_xlsx['updTs'], format='%Y-%m-%d %H:%M:%S')
    up_record_xlsx['交易时间'] = pd.to_datetime(up_record_xlsx['交易时间'], format='%Y-%m-%d %H:%M:%S')
    up_xlsx['dealTime'] = pd.to_datetime(up_xlsx['dealTime'], format='%Y-%m-%d %H:%M:%S')

    '''get yun order not up'''
    is_up = up_record_xlsx['银商订单号'].isin(up_xlsx.loc[:, 'merchantOrderId'])
    up_record_match = up_record_xlsx[is_up]
    up_record_missing = up_record_xlsx[~is_up]

    # t = datetime(2026, 10, 20)
    t = datetime.today()-timedelta(days=3)
    up_record_missing = up_record_missing.filter(pd.col('加单时间') < t)
    up_record_missing = simplify_up_record_excel(up_record_missing)

    return up_record_missing

def check_missing_union_pay(yun_order_25, up_xlsx, flag_debug=True):
    if flag_debug: print('num yun ', len(yun_order_25), 'num up ', len(up_xlsx))
    # up_xlsx['updTs'] = pd.to_datetime(up_xlsx['updTs'], format='%Y-%m-%d %H:%M:%S')
    up_xlsx['dealTime'] = pd.to_datetime(up_xlsx['dealTime'], format='%Y-%m-%d %H:%M:%S')
    yun_order_25['加单时间'] = pd.to_datetime(yun_order_25['加单时间'], format='%Y-%m-%d %H:%M:%S')

    '''get yun order not up'''
    is_up = yun_order_25['合同号'].isin(up_xlsx.loc[:, 'auditOrderId'])
    yun_match = yun_order_25[is_up]
    yun_missing = yun_order_25[~is_up]

    # t = datetime(2026, 10, 20)
    t = datetime.today()
    yun_missing = yun_missing.filter(pd.col('加单时间') < t)
    yun_missing = simplify_yun_excel(yun_missing)

    if flag_debug:
        print('num yun ', len(is_up))
        print('九讯云侧未上传银联 '+str(len(yun_missing))+'个 开始')
        print(yun_missing.to_string(index=False, show_dimensions=False))
        # yun_missing.to_excel(writer, sheet_name='九讯云订单对应不到银联')
        print('九讯云侧未上传银联 结束\n')

    '''get up order not in 9yun'''
    is_yun = up_xlsx['auditOrderId'].isin(yun_order_25['合同号'])
    up_missing = up_xlsx[~is_yun]

    # t = datetime(2026,9,1)
    t = datetime(2026,1,1)
    up_audit_id_missing = up_missing.filter(pd.col('dealTime') > t)
    # up_audit_id_missing = up_missing.filter(pd.col('updTs') > t)
    # up_audit_id_missing = up_missing.filter(pd.col('dealTime') > t)
    up_audit_id_missing = simplify_up_excel(up_audit_id_missing, yun_order_25)

    if flag_debug:
        print('num up ', len(is_yun))
        print('银联上传对应不到九讯云 '+str(len(up_audit_id_missing))+'个 开始')
        print(up_audit_id_missing.to_string(index=False, show_dimensions=False))
        # up_audit_id_missing.to_excel(writer, sheet_name='银联订单对应不到九讯云')
        print('银联上传对应不到九讯云 结束\n')

    return yun_missing, up_audit_id_missing

def check_missing_union_pay_(yun_order_25, up_order):
    json_keys = list(up_order.keys())
    is_up = yun_order_25['合同号'].isin(json_keys)
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

    return up_audit_id_missing

def check_up_rejected_late_order(yun_order_25, up_xlsx):
    # yun_order_json = excel_to_json(yun_order_25, '合同号')
    '''get up order rejected'''
    up_rejected = up_xlsx.filter(pd.col('auditRoleNm')=='2026年陕西数码市级线下复审')
    up_rejected = up_rejected.filter(pd.col('auditInfo')!='通过')
    up_rejected = up_rejected.filter(pd.col('auditInfo')!='通过通过')
    up_rejected = simplify_up_excel(up_rejected, yun_order_25)

    print('提交银联失败 '+ str(len(up_rejected)) + '个 开始')
    print(up_rejected.to_string(index=False, show_dimensions=False))
    # up_rejected.to_excel(writer, sheet_name='银联审核不过')
    print('提交银联失败 结束\n')

    '''get up order out of time'''
    up_xlsx['updTs'] = pd.to_datetime(up_xlsx['updTs'], format='%Y-%m-%d %H:%M:%S')
    t = datetime.today()- timedelta(days=7)
    # t = datetime(2026,10,20)
    print('up_xlsx', len(up_xlsx))
    # up_oot = up_xlsx.filter(pd.col('auditRoleNm').str.contains('初审'))
    up_oot = up_xlsx.filter(~pd.col('auditRoleNm').str.contains('复审'))
    # up_oot = up_xlsx[~up_xlsx['auditRoleNm'].astype(str).str.contains('复审')]

    # up_oot = up_xlsx.filter(pd.col('auditRoleNm').str.contains('初审'))
    # up_oot = up_xlsx.filter(pd.col('auditRoleNm')=='2026年陕西数码市级线下初审')
    # up_oot = pd.concat([up_oot, up_xlsx.filter(pd.col('auditRoleNm')=='')])
    # up_oot = up_oot.filter(pd.col('updTs') < t)
    up_oot = simplify_up_excel(up_oot, yun_order_25)

    print('银联审核超时 '+ str(len(up_oot)) + '个 开始')
    print(up_oot.to_string(index=False, show_dimensions=False))
    # up_oot.to_excel(writer, sheet_name='银联审核超时')
    print('银联审核超时 结束\n')

    # up_audit_id_oot_per_company = {'陕西恒檀通信有限公司':{}, '陕西恒国通信有限公司':{}, '商洛市商州区宁致远通讯部':{}, '南洛市商州区宁致远通讯部':{}}

    return up_rejected, up_oot

def gov_sub_order_to_excel(yun_xlsx_fp='E:/share/unionpay_revise/国补订单明细_恒檀.xlsx',
                           up_xlsx_fp='E:/share/unionpay_revise/云闪付提交状态_恒檀.xlsx',
                           out_xlsx_fp='E:/share/unionpay_revise/国补修正_恒檀.xlsx'):
    # up_dp = pathlib.Path('E:/share/unionpay_revise/')
    # dp_xlsx = dp_day.joinpath('国补订单明细.xlsx')
    yun_xlsx = pd.read_excel(pathlib.Path(yun_xlsx_fp), dtype=str,skipfooter=1)
    # yun_xlsx = pd.read_excel(pathlib.Path(fp), dtype=str,skipfooter=1)
    up_xlsx_hengtan = pd.read_excel(pathlib.Path(up_xlsx_fp), sheet_name='records', dtype=str, skipfooter=0, na_filter=False)
    up_record_xlsx_hengtan = pd.read_excel(pathlib.Path('E:/share/unionpay_revise/银联流水_恒檀.xlsx'), dtype=str, skipfooter=3, na_filter=False)

    bank_id = up_record_xlsx_hengtan.loc[:, '银商订单号']
    print('bank_id', bank_id)

    up_xlsx_hengtan['saleName'] = up_xlsx_hengtan['saleName'].apply(simplify_name)
    print('up_xlsx_hengtan', len(up_xlsx_hengtan))

    yun_audit_id_unique_xlsx, dup_rows = check_repeat_audit_id(yun_xlsx)
    order_audit_id_25dig, order_audit_id_not25_simp = check_audit_id_num(yun_audit_id_unique_xlsx)

    yun_missing, up_audit_id_missing = check_missing_union_pay(order_audit_id_25dig, up_xlsx_hengtan)
    check_unload_union_pay(up_record_xlsx_hengtan, up_xlsx_hengtan, flag_debug=True)
    yun_missing, up_audit_id_missing = check_missing_union_pay(order_audit_id_25dig, up_xlsx_hengtan)

    up_rejected, up_oot = check_up_rejected_late_order(order_audit_id_25dig, up_xlsx_hengtan)

    # gov_subsidy_order_yun_id = yun_xlsx.set_index("订单号").to_dict(orient="index")
    with pd.ExcelWriter(pathlib.Path(out_xlsx_fp)) as writer:
    # with pd.ExcelWriter('E:/share/unionpay_revise/output/国补修正_恒檀.xlsx') as writer:
        order_audit_id_not25_simp.to_excel(writer, sheet_name='外部订单号错位', index=False)
        dup_rows.to_excel(writer, sheet_name='九讯云外部订单号重复', index=False)
        yun_missing.to_excel(writer, sheet_name='九讯云订单对应不到银联', index=False)
        up_audit_id_missing.to_excel(writer, sheet_name='银联上传对应不到九讯云', index=False)
        up_rejected.to_excel(writer, sheet_name='银联审核不过', index=False)
        up_oot.to_excel(writer, sheet_name='银联审核超时', index=False)
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yun_xlsx_fp", type=str, help="the absolute path from 9yun")
    parser.add_argument("--up_xlsx_fp", type=str, help="the absolute path from union pay")
    parser.add_argument("--out_xlsx_fp", type=str, help="the absolute path for output excel")
    # parser.add_argument("--dir", type=str, help="the absolute path that contain orders for a day")
    args = parser.parse_args()
    gov_sub_order_to_excel(args.yun_xlsx_fp, args.up_xlsx_fp)
    return

if __name__ == '__main__':
    main()