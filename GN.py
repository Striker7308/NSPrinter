import os, io
import base64
import requests
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv


def get_img(img):
    load_dotenv()
    flag_debug = False

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    ### load model info
    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    api_key = os.getenv("VOLC_ARK_GEN_API_KEY")

    ### build request
    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": "根据输入签名图，生成一张签名PNG，全透明背景，形式可以是RGBA",
        "image": f"data:image/jpeg;base64,{image_base64}",
        "n": "1",
        "size": "1K",
        "watermark": False
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    ### send request
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    ### get result img URL
    print(result)
    image_url = result["data"][0]["url"]
    img_data = requests.get(image_url)
    pil_img = Image.open(io.BytesIO(img_data.content))

    if flag_debug:
        print(f"img url：{image_url}")
        with open('./signature_clean.png', 'wb') as f:
            f.write(img_data.content)

    return pil_img

def main():
    # 1. 读取本地图片并转为 Base64
    image_path = "./re_signature.jpg"
    img = Image.open(image_path)

    img = get_img(img)
    print('signature size', img.size)

if __name__ == '__main__':
    main()