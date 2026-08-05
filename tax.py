import json

def get_tax_json(jiuxun, invoice, store):
    total_amount_including_tax = float(invoice.get('total_amount_including_tax', 0))
    tax_rate = store.get(jiuxun['销方公司名称'], {}).get('tax_rate', 0.01)
    amount_invoice = total_amount_including_tax / (1+tax_rate)
    amount_tax = round(amount_invoice * tax_rate, 2)
    amount_invoice = total_amount_including_tax - amount_tax
    tax = {
        "发票号码": invoice.get('invoice_number', ''),
        "发票类型": '数电普票',
        "开票日期": invoice.get('issue_date', ''),
        "数量": '1',
        "发票金额": str(amount_invoice),
        "税额": str(amount_tax),
        "销售方纳税人识别号": store.get(jiuxun['销方公司名称'], {}).get('code', '未登记'),
        "企业名称": jiuxun['销方公司名称'],
        "开票人姓名：": jiuxun['发票抬头'],
    }
    return tax

def main():
    return

if __name__ == '__main__':
    main()
