import json

from OCR import client, model
from PIL import Image, ImageDraw, ImageEnhance
import base64

def get_sn(img_fp):
    fo = open(img_fp, "rb")
    image_base64 = base64.b64encode(fo.read()).decode("utf-8")
    image_format = Image.open(img_fp).format.lower()
    messages = [{
        "role": "user",
        "content":
            [{"type": "image_url","image_url": f"data:image/{image_format};base64,{image_base64}"},
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
