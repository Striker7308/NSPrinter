import json

from OCR import client, model
from PIL import Image, ImageDraw, ImageEnhance
import base64

from utils.format import image_to_openai_b64


def get_id(img_fp):
    flag_debug = False
    id = {}

    if flag_debug: print(img_fp)
    openai_b64 = image_to_openai_b64(img_fp)
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
    id_json = json.loads(content)
    for k, v in id_json.items():
        if k.find('名') != -1: id['name'] = v
        if k.find('号') != -1: id['num'] = v
    assert len(id["num"]) == 18
    return id


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
