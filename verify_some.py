import argparse
from verify import check_one_day
import pathlib

def verify(order_ids):
    root_dp = 'E:/share/'
    root_path = pathlib.Path(root_dp)
    order_ids = set(order_ids)
    order_dps = []
    for p in root_path.rglob('*'):
        if p.is_dir() and '国补订单附件' in p.as_posix() and p.name.split('（')[0] in order_ids:
            order_dps.append(p.resolve())

    check_one_day()
    return order_dps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order_ids", type=str, help="the absolute path that contain orders for a day")
    args = parser.parse_args()
    verify(args.order_ids)
    return


if __name__ == '__main__':
    main()
