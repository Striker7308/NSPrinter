import json
import pathlib
from utils.filepath import find_jiuxun_fp

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

def get_jiuxun(dp):
    dp = pathlib.Path(dp)
    jiuxun_fp = find_jiuxun_fp(dp)
    jiuxun = get_jiuxun_info(jiuxun_fp)
    return jiuxun

def main():
    get_jiuxun_info()

if __name__ == '__main__':
    main()