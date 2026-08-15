import json

def load_dict_txt(fp='./imgs/国补订单附件-pinpai/10224732（未审核）/10224732订单信息.txt'):
    flag_debug = False
    #TODO:
    data_txt = {}
    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            k, v = line.split("：", 1)
            data_txt[k.strip()] = v.strip()
            if k.strip() == '发票备注':
                v = v.strip()
                i_start = v.find('购买方地址')
                i_end = v.find('，', i_start)
                data_txt['customer_address'] = v[i_start+6:i_end]
        f.close()

    if flag_debug: print(json.dumps(data_txt, indent=2, ensure_ascii=False))

    return data_txt

def dump_list_txt(the_list, fp):
    with open(fp, 'w', encoding='utf-8') as f:
        f.write("\n".join(the_list))
    f.close()
    return

def dict2list(the_dict, the_list):
    the_list = the_list + [the_dict.current.key] if type(the_dict) == dict else dict2list(the_dict.current.key, the_list)
    return

def load_list_txt(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()
    return text.splitlines()