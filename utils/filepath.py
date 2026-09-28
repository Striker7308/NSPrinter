import os, pathlib
import warnings
import json
from datetime import datetime, timedelta


def find_invoice_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('dzfp*.pdf')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'invoice pdf path does not exist in {dp}', UserWarning)
    return fp

def find_jiuxun_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('*订单信息.txt')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'jiuxun txt file does not exist in {dp}', UserWarning)
    return fp

def find_id_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('身份证照片*')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'id img does not exist in {dp}', UserWarning)
    return fp

def find_receipt_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('销售小票及刷卡小票*')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'receipt img does not exist in {dp}', UserWarning)
    return fp

def find_phone_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('机身串码及SN码截屏*')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'phone img does not exist in {dp}', UserWarning)
    return fp

def find_in_progress_order_fp(dp_day):
    dp_day = pathlib.Path(dp_day)
    today_16 = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    today_2050 = datetime.now().replace(hour=20, minute=50, second=0, microsecond=0)
    # date = (datetime.now()).strftime("%Y%m%d")

    dp_xlsx = dp_day.joinpath('订单列表.xlsx')
    return dp_xlsx


def main():
    # pdf_fp = find_invoice_fp()
    # print(pdf_fp)
    return

if __name__ == '__main__':
    main()