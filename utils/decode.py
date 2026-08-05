import json

import PIL
import zxingcpp
from PIL import Image, ImageDraw, ImageEnhance
from utils.geometry import format_barcodes
import cv2

def decode_qr_robust(img):
    use_global_binarizer = True

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    # 轻微降噪，消除屏幕摩尔纹噪点
    gray = cv2.GaussianBlur(gray, (3, 3), 0.6)
    img_view = zxingcpp.ImageView(gray.tobytes(), gray.shape[1], gray.shape[0], zxingcpp.ImageFormat.Lum)

    source = zxingcpp.CreateLuminanceSource(img_view)
    if use_global_binarizer:
        binarizer = zxingcpp.GlobalHistogramBinarizer(source)
    else:
        binarizer = zxingcpp.HybridBinarizer(source)

    bitmap = zxingcpp.BinaryBitmap(binarizer)
    reader = zxingcpp.MultiFormatReader()
    # 关键！高层read_barcode默认关闭这两个
    reader.try_harder = True
    reader.try_rotate = True

    try:
        result = reader.decode(bitmap)
        return result
    except zxingcpp.NotFoundException:
        return None

    return

def decode_qr(img):
    # print(f"支持的格式: {zxingcpp.barcode_formats_list()}")
    flag_debug = False
    if flag_debug:
        print(f"📐 尺寸: {img.size}")
        print(f"🎨 模式: {img.mode}")

    # 尝试不同处理方式
    strategies = [
        ("原始图片", img),
        ("灰度图", img.convert('L')),
        # ("增强对比度", ImageEnhance.Contrast(img).enhance(2.0)),
        # ("增强对比度+锐化", ImageEnhance.Sharpness(ImageEnhance.Contrast(img).enhance(2.0)).enhance(2.0)),
        # ("二值化", img.convert('1')),
    ]

    for name, processed_img in strategies:
        try:
            results = zxingcpp.read_barcodes(processed_img)
            if len(results) == 5:
                # print(f"✅ [{name}] 解码成功!")
                # for r in results:
                #     print(f"   格式: {r.format}, 内容: {r.text}")
                return format_barcodes(results)
            else:
                print(f"❌ [{name}] 解码失败")
                print('get', len(results), 'barcodes')
                for result in results:
                    print(result.text)
        except Exception as e:
            print(f"⚠️ [{name}] 错误: {e}")
    return format_barcodes(results)

def decode_qr_opencv(img):
    flag_debug = True
    if flag_debug:
        print(f"📐 尺寸: {img.shape}")
        # print(f"🎨 模式: {img.mode}")
    print('cv2.__version__:', cv2.__version__)
    detect_obj = cv2.wechat_qrcode_WeChatQRCode()

    res, points = detect_obj.detectAndDecode(img)
    print('res:', res)
    print('res len', len(res))
    print('points len:', len(points))

    results = zxingcpp.read_barcodes(img)
    for result in results:
        print(result.text)
    return results

def parse_invoice_qr(qr_string):
    """
    解析数电普票二维码字符串
    Args:
        qr_string: 如 "01,32,,26612000001370829031,4099.00,20260710,,4D8B"
    Returns:
        dict: 解析后的字段字典
    """
    # seg with ,
    parts = qr_string.split(',')
    assert len(parts) == 8
    assert len(parts[3]) == 20, 'invoice should be 20 digits, but get'+str(len(parts[3]))

    result = {
        "invoice_type": parts[0],
        "provincial_administrative_division_code": parts[1],
        "invoice_code": parts[2],
        "invoice_number": parts[3],
        "total_amount_including_tax": parts[4],
        "issue_date": parts[5],
        "verification_code": parts[6],
        "short_checksum_code": parts[7],
    }
    return result

def parse_receipt_qr(qr_string):
    """
    decode third qr code from receipt
    Args:
        qr_string: like 0020260629151347006431419+898611008079470+1G4VV0GW+20260629+18300761240N+20260629151851452044418946
    Returns:
        dict: decoded data formate as map
    """
    # seg with ,
    parts = qr_string.split('+')
    assert len(parts) == 6
    assert len(parts[0]) == 25, 'invoice should be 20 digits, but get' + str(len(parts[0]))

    result = {
        "external_order_id": parts[0],
        "merchant_id": parts[1],
        "end_id": parts[2],
        "data": parts[3],
        "reference_id": parts[4],
        "bank_order_id": parts[5],
    }
    return result

def main():
    img = cv2.imread(r'./c.jpg')
    print(img.shape)
    decode_qr_robust(img)
    pass

if __name__ == '__main__':
    main()