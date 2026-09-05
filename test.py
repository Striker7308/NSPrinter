import re

def main():
    info = 'iPhone17BLACK256GB[SN号:D1QH7D724P,IMEI_1:352173919835065,IMEI_2:352173919327519,型号:MG774CH/A]'
    sn_match = re.search(r'SN(?:号)?\s*:\s*([^,]+)', info)
    print(sn_match.group(1))

if __name__ == '__main__':
    main()