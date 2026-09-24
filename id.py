import json

from OCR import client, model
from PIL import Image, ImageDraw, ImageEnhance
import base64

from utils.format import image_to_openai_b64, img2openai_b64
from utils.geometry import resize_for_doubao


def get_id(img_fp, flag_debug=False):
    id_json = {'name': '不识别', 'num': '不识别', 'address': '不识别'}

    if flag_debug: print(img_fp)
    img = Image.open(img_fp)
    img = resize_for_doubao(img)
    openai_b64 = img2openai_b64(img)

    messages = [{
        "role": "user",
        "content":
            [{"type": "image_url","image_url": openai_b64},
            {"type": "text", "text": "这是身份证照片吗，缺失的也算是，是的话，提取姓名,身份证号，和地址，以json格式返回，不是的话，直接返回No"}]
    }]

    extra_body = {
        "thinking": {"type": "disabled"},
        "reasoning_effort": "minimal"
    }
    # extra_body = {"thinking": {"type": "enabled"}}
    # extra_body = {"thinking": {"type": "auto"}}
    # content = '{"名": "徐辉","名": "61250118210200218","地": "徐辉"}'
    completion = client.chat.completions.create(
        extra_body=extra_body,
        messages=messages,
        max_tokens=4096,
        stream=False,
        model=model,
    )
    content = completion.choices[0].message.content
    if flag_debug: print(content)
    if content == 'No': return id_json
    try:
        id_det = json.loads(content)
        for k, v in id_det.items():
            if k.find('名') != -1: id_json['name'] = v
            if k.find('号') != -1: id_json['num'] = v
            if k.find('地') != -1: id_json['address'] = v
        # assert len(id_json["num"]) == 18
    except Exception as e:
        print('id解析错误')
        print(img_fp)
        print(' '*int((len(img_fp)+len(content))/4)+'vvv')
        print(content)
        print(e)
        # return {'id识别错误': content}

    return id_json, content


def test_id():
    image_file = 'E:/share/国补订单附件20260921/10236650（未审核）/身份证照片.jpg'
    # image_file = './imgs/1/id.jpg'
    id_json = get_id(image_file, True)
    print(json.dumps(id_json, indent=2, ensure_ascii=False))
    return id_json


def main():
    print('Hello World')
    test_id()


if __name__ == '__main__':
    main()
