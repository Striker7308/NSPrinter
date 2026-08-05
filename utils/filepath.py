import os, pathlib
import warnings


def find_invoice_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('dzfp*.pdf')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'invoice file path does not exist in {dp}', UserWarning)
    return fp

def find_jiuxun_fp(dp='./../imgs/10219792（未审核）/'):
    dp = pathlib.Path(dp)
    fps = dp.glob('*订单信息.txt')
    fp = next(fps, None)
    if fp is None:
        warnings.warn(f'jiuxun file path does not exist in {dp}', UserWarning)
    return fp

def main():
    # pdf_fp = find_invoice_fp()
    # print(pdf_fp)
    return

if __name__ == '__main__':
    main()