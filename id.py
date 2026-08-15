import json

from OCR import client, model
from PIL import Image, ImageDraw, ImageEnhance
import base64

from utils.format import image_to_openai_b64, img2openai_b64
from utils.geometry import resize_for_doubao

def get_id(img_fp):
    flag_debug = False
    id_json = {}

    if flag_debug: print(img_fp)
    img = Image.open(img_fp)
    img = resize_for_doubao(img)
    openai_b64 = img2openai_b64(img)

    messages = [{
        "role": "user",
        "content":
            [{"type": "image_url","image_url": openai_b64},
            {"type": "text", "text": "照片是身份证吗,不是的话,只返回No, 如果是,提取姓名和身份证号,json格式返回"}]
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
    if content == 'No': return {
        'name': '不识别',
        'num': '不识别',
    }
    id_det = json.loads(content)
    for k, v in id_det.items():
        if k.find('名') != -1: id_json['name'] = v
        if k.find('号') != -1: id_json['num'] = v
    assert len(id_json["num"]) == 18
    return id_json


def test_id():
    image_file = './imgs/1/id.jpg'
    id_json = get_id(image_file)
    print(json.dumps(id_json, indent=2, ensure_ascii=False))
    return id_json

def main():
    print('Hello World')
    test_id()

if __name__ == '__main__':
    main()
