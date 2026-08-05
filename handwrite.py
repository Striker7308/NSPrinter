from OCR import client, model
import json


def generate_handwriting(txt=''):
    data = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": "生成狗狗趴在草地上的近景画面",
        "image": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimage.png",
        "size": "2K",
        "sequential_image_generation": "disabled",
        "stream": False,
        "response_format": "url",
        "watermark": False
    }
    messages = [{
        "role": "user",
        "content":
            [{"type": "text", "text": "我告诉你汉字，你可以生成坐标序列模仿手写吗"}]
    }]
    extra_body = {"thinking": {"type": "disabled"}}

    completion = client.chat.completions.create(
        extra_body=extra_body,
        messages=messages,
        max_tokens=4096,
        stream=False,
        model=model,
    )
    content = completion.choices[0].message.content
    print(content)
    id_json = json.loads(content)
    return id_json

def test_id():
    txt = ''
    id_json = generate_handwriting(txt)
    print(json.dumps(id_json, indent=2, ensure_ascii=False))
    return id_json

def main():
    print('Hello World')
    test_id()

if __name__ == '__main__':
    main()