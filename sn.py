import json

from OCR import client, model
from PIL import Image, ImageDraw, ImageEnhance
import base64

from utils.format import image_to_openai_b64

def get_sn(img_fp):
    flag_debug = False
    openai_b64 = image_to_openai_b64(img_fp)

    messages = [{
        "role": "user",
        "content":
            [{"type": "image_url","image_url": openai_b64},
            {"type": "text", "text": "提取IMEI1，IMEI2，SN码，严格按照 {\"IMEI1\": , \"IMEI2\": , \"SN\": }json格式返回"}]
    }]

    extra_body = {"thinking": {"type": "disabled"}}
    # extra_body = {"thinking": {"type": "enabled"}}
    # extra_body = {"thinking": {"type": "auto"}}

    completion = client.chat.completions.create(
        extra_body=extra_body,
        messages=messages,
        max_tokens=4096,
        stream=False,
        model=model,
    )
    content = completion.choices[0].message.content
    if flag_debug: print(content)
    sn_json = json.loads(content)
    return sn_json


def test_sn():
    image_file = './imgs/1/sn.jpg'
    sn_json = get_sn(image_file)
    print(json.dumps(sn_json, indent=2, ensure_ascii=False))
    return


def main():
    print('Hello World')
    test_sn()


if __name__ == '__main__':
    main()
