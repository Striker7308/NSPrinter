import base64
import copy
import os, io
import re
import json

import cv2
from openai import OpenAI
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import zxingcpp

from utils.decode import parse_invoice_qr, parse_receipt_qr, decode_qr, decode_qr_opencv
from utils.geometry import polygon_to_xyxy, transform_polygon, clean_signature_to_binary
from OCR import client, model

def draw_bbox(img, barcodes, fp='./re_bbox.jpg'):
    flag_debug = False
    if flag_debug:
        print(barcodes[2].format)
        print(barcodes[2].position)
        print(type(barcodes[2].position))
        print(barcodes[2].position.top_left.x)
        print(barcodes[2].position.top_left.y)
        print(barcodes[2].orientation)
        print(barcodes[2].text)
        print(type(barcodes[2].text))

    draw = ImageDraw.Draw(img)
    for barcode in barcodes:
        points = []
        bbox = barcode.position
        points.append(bbox.top_left.x)
        points.append(bbox.top_left.y)
        points.append(bbox.top_right.x)
        points.append(bbox.top_right.y)
        points.append(bbox.bottom_right.x)
        points.append(bbox.bottom_right.y)
        points.append(bbox.bottom_left.x)
        points.append(bbox.bottom_left.y)
        # points.append([bbox.top_left.x, bbox.top_left.y])
        # points.append([bbox.top_right.x, bbox.top_right.y])
        # points.append([bbox.bottom_right.x, bbox.bottom_right.y])
        # points.append([bbox.bottom_left.x, bbox.bottom_left.y])
        draw.polygon(points, outline='red', width=3)
    img.save(fp)
    return img


def get_receipt_rich_txt_bbox(img, upper_barcode, lower_barcode):
    """get rich txt image cropped"""
    # draw = ImageDraw.Draw(img)
    '''get rich text info from receipt'''
    ### get rich text bbox
    x_top_left, y_top_left = int(upper_barcode.position.bottom_left.x), int(upper_barcode.position.bottom_left.y)
    x_top_right, y_top_right = int(upper_barcode.position.bottom_right.x), int(upper_barcode.position.bottom_right.y)
    x_bottom_right, y_bottom_right = int(lower_barcode.position.top_right.x), int(lower_barcode.position.top_right.y)
    x_bottom_left, y_bottom_left = int(lower_barcode.position.top_left.x), int(lower_barcode.position.top_left.y)

    w, h = x_top_right-x_top_left, y_bottom_left-y_top_left
    # print(w, h)
    w = w+w/2

    x_top_left, x_bottom_left = x_top_left-w/4, x_bottom_left-w/4
    x_top_right, x_bottom_right = x_top_right+w/4, x_bottom_right+w/4

    points = []
    points.append([x_top_left, y_top_left])
    points.append([x_top_right, y_top_right])
    points.append([x_bottom_right, y_bottom_right])
    points.append([x_bottom_left, y_bottom_left])

    # draw.polygon(points, outline='green', width=3)
    # img.save('./re_bbox.jpg')

    return points

def get_receipt_rich_txt_img(img, upper_barcode, lower_barcode):
    """get rich txt image cropped"""
    points = get_receipt_rich_txt_bbox(img, upper_barcode, lower_barcode)
    ### extract rich text area
    bbox = polygon_to_xyxy(points)
    img_rich_txt = img.crop(bbox)
    # img_rich_txt.save('./re_rich_txt.jpg')
    return img_rich_txt


def get_receipt_signature(img, upper_barcode, lower_barcode):
    """get signature image cropped"""
    points_rich_txt = get_receipt_rich_txt_bbox(img, upper_barcode, lower_barcode)
    ### extract signature area
    print(points_rich_txt)
    points_signature = transform_polygon(points_rich_txt, scale_x=0.4, scale_y=0.15, dx_ratio=0.25, dy_ratio=0.23)
    # points_signature[0]
    bbox = polygon_to_xyxy(points_signature)

    img_copy = copy.deepcopy(img)
    draw = ImageDraw.Draw(img_copy)
    # draw.polygon(points_signature, outline='red', width=3)
    # draw.polygon(points_rich_txt, outline='red', width=3)
    img_copy.save('./re_bbox.jpg')

    img_signature = img.crop(bbox)
    img_signature = img_signature.resize((img_signature.width, img_signature.height))
    # img_signature = img_signature.resize((img_signature.width*10, img_signature.height*10))
    img_signature.save('./re_signature.jpg')
    return img_signature


def parse_device_info(text):
    """
    Parse device info string into structured data
    Args:
        text: "华为畅享90ProMax8GB+256GB曜金黑双卡全网通版[SN:6UNBB26429295358,IMEI_1:864910089395938,IMEI_2:864910089435932,型号:CHZ-AL00]"
    Returns:
        dict with name, sn, imei_1, imei_2, type
    """
    # Extract the main name (everything before '[')
    if '[' in text:
        name = text.split('[')[0].strip()
    else:
        name = text.strip()

    # Extract bracketed info
    bracket_match = re.search(r'\[(.*?)\]', text)
    if not bracket_match:
        return {"name": name}

    info = bracket_match.group(1)

    # Parse key:value pairs
    result = {"name": name}

    # SN
    sn_match = re.search(r'SN:([^,]+)', info)
    if sn_match:
        result["SN"] = sn_match.group(1)

    # IMEI_1
    imei1_match = re.search(r'IMEI_1:([^,]+)', info)
    if imei1_match:
        result["IMEI1"] = imei1_match.group(1)

    # IMEI_2
    imei2_match = re.search(r'IMEI_2:([^,]+)', info)
    if imei2_match:
        result["IMEI2"] = imei2_match.group(1)

    # type
    type_match = re.search(r'型号:([^,]+)', info)
    if type_match:
        result["type"] = type_match.group(1)

    return result


def get_rich_txt_by_Doubao(img_rich_txt):
    flag_debug = True

    image_ref_file = './imgs/ref/re.jpg'
    img_ref = Image.open(image_ref_file)
    barcodes_ref = decode_qr(img_ref)
    draw_bbox(img=img_ref, barcodes=barcodes_ref, fp='./ref_bbox.jpg')
    img_ref_rich_txt = get_receipt_rich_txt_img(img_ref, barcodes_ref[2], barcodes_ref[3])
    if flag_debug: img_ref_rich_txt.save('./ref_rich_txt.jpg')

    buffer = io.BytesIO()
    img_rich_txt.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_format = 'jpeg'

    buffer = io.BytesIO()
    img_ref_rich_txt.save(buffer, format='JPEG')
    image_ref_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_format = 'jpeg'

    # get prompt
    receipt_txt_prompt = {}
    with open('./config/receipt_rich_txt.json', 'r', encoding='utf-8') as f:
        receipt_txt_prompt = json.load(f)
        f.close()

    if flag_debug: print('receipt_txt_prompt:\n', receipt_txt_prompt)

    target_base64 = image_base64
    ref_base64 = image_ref_base64
    prompt_text = f"将第一张图片转为json，参考第二张图片和其对应的json数据:{json.dumps(receipt_txt_prompt, ensure_ascii=False, indent=2)},严格按照以上格式从第一张图片中提取信息，以JSON返回。"

    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{target_base64}"},  # Target image (to extract)
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{ref_base64}"}, # Reference image (with annotations)
            {"type": "text", "text": prompt_text},
        ]
    }]
    extra_body = {"thinking": {"type": "disabled"}}

    completion = client.chat.completions.create(
        extra_body=extra_body,
        messages=messages,
        max_tokens=8192,
        stream=False,
        model=model,
    )

    rich_txt = completion.choices[0].message.content
    if flag_debug: print('respond content:\n', rich_txt)
    rich_txt = rich_txt.replace('\\n', '')
    receipt_txt_json = json.loads(rich_txt)
    receipt_txt_json['phone_info'] = parse_device_info(receipt_txt_json['商品'])
    for key, value in receipt_txt_json['第三方优惠说明'].items():
        print(key, value)
        if key.find('支付') != -1:
            receipt_txt_json['pay'] = value
        elif key.find('线下优惠') != -1:
            receipt_txt_json['national_saving'] = value
        elif key.find('银行消费券') != -1:
            receipt_txt_json['bank_saving'] = value
        else:
            raise KeyError(key+' not in receipt pay and saving info key')
    return receipt_txt_json

def get_signature(img_fp='imgs/0/re.jpg'):
    img = Image.open(img_fp)
    barcodes = decode_qr(img)
    img_signature = get_receipt_signature(img, barcodes[2], barcodes[3])
    signature_img = clean_signature_to_binary(img_signature)
    return signature_img

def get_receipt(image_file):
    ### get qr code
    flag_debug = True

    img = Image.open(image_file)
    if flag_debug: img.save('./re.jpg')

    barcodes = decode_qr(img)
    if len(barcodes) != 5: print('decoding fail, img fp', image_file)
    if flag_debug:
        print(image_file)
        # print(len(barcodes))
        # print(barcodes[0].text)
        # print(barcodes[1].text)
        # print(barcodes[2].text)
        # print(barcodes[3].text)
        # print(barcodes[4].text)
    receipt_qrcode_json = parse_receipt_qr(barcodes[2].text)
    draw_bbox(img=img, barcodes=barcodes, fp='./re_bbox.jpg')

    '''get rich text info from receipt'''
    img_rich_txt = get_receipt_rich_txt_img(img, barcodes[2], barcodes[3])
    if flag_debug: img_rich_txt.save('./re_rich_txt.jpg')

    receipt_txt_json = get_rich_txt_by_Doubao(img_rich_txt)
    if flag_debug: print(json.dumps(receipt_txt_json, indent=2, ensure_ascii=False))


    img_signature = get_receipt_signature(img, barcodes[2], barcodes[3])
    signature_img = clean_signature_to_binary(img_signature)

    return {**receipt_qrcode_json, **receipt_txt_json}, signature_img

def get_receipt_prcode(image_file):
    flag_debug = True
    img = cv2.imread(image_file)
    if flag_debug: cv2.imwrite('./re.jpg', img)
    decode_qr_opencv(img)
    return

def test_signature():
    image_file = './imgs/ref/re.jpg'

    img = Image.open(image_file)

    barcodes = decode_qr(img)

    '''get signature from receipt'''
    img_signature = get_receipt_signature(img, barcodes[2], barcodes[3])
    signature = clean_signature_to_binary(img_signature)
    signature.save('./signature_cv.jpg')
    # draw_bbox(img=img, barcodes=barcodes, fp='./re_signature.jpg')
    return

def test_receipt():
    # print(f"支持的格式: {zxingcpp.barcode_formats_list()}")

    ### get qr code
    image_file = './imgs/1/c.jpg'
    # receipt_json, signature_img = get_receipt(image_file)
    receipt_json = get_receipt_prcode(image_file)
    print(json.dumps(receipt_json, indent=2, ensure_ascii=False))
    return


def main():
    print('Hello World')
    # test_signature()
    test_receipt()
    # phone_info = parse_device_info('华为畅享90ProMax8GB+256GB曜金黑双卡全网通版[SN:6UNBB26429295358,IMEI_1:864910089395938,IMEI_2:864910089435932,型号:CHZ-AL00]')
    # print(phone_info)

if __name__ == '__main__':
    main()