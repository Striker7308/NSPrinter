from openai import OpenAI

import json
import base64
import os
from dotenv import load_dotenv
import os
import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import urllib, urllib3, sys, uuid

load_dotenv()
llm_config = {
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "api_key": os.getenv("VOLC_ARK_API_KEY"),
    "model": "doubao-seed-1-8-251228"
}

base_url = llm_config.get("base_url")
api_key = llm_config.get("api_key")
model = llm_config.get("model")

# 初始化OpenAI客户端
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# def parse_bbox(bbox_str):
#     """
#     解析 <bbox>262 300 612 395</bbox> 格式
#     返回: [262, 300, 612, 395]
#     """
#     # 方法1: 使用 re.findall 提取数字
#     numbers = re.findall(r'\d+', bbox_str)
#     return [int(n) for n in numbers]


def test_aliyun():
    # -*- coding: utf-8 -*-
    context = ssl._create_unverified_context()

    def get_img(img_file):
        """将本地图片转成base64编码的字符串，或者直接返回图片链接"""
        # 简单判断是否为图片链接
        if img_file.startswith("http"):
            return img_file
        else:
            with open(os.path.expanduser(img_file), 'rb') as f:  # 以二进制读取本地图片
                data = f.read()
        try:
            encodestr = str(base64.b64encode(data), 'utf-8')
        except TypeError:
            encodestr = base64.b64encode(data)

        return encodestr

    def posturl(headers, body):
        """发送请求，获取识别结果"""
        try:
            params = json.dumps(body).encode(encoding='UTF8')
            req = Request(REQUEST_URL, params, headers)
            r = urlopen(req, context=context)
            html = r.read()
            return html.decode("utf8")
        except HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))

    def request(appcode, img_file, params):
        # 请求参数
        if params is None:
            params = {}
        img = get_img(img_file)
        if img.startswith('http'):  # img 表示图片链接
            params.update({'url': img})
        else:  # img 表示图片base64
            params.update({'img': img})

        # 请求头
        headers = {
            'Authorization': 'APPCODE %s' % appcode,
            'Content-Type': 'application/json; charset=UTF-8'
        }

        response = posturl(headers, params)
        json_response = json.loads(response)
        print(json.dumps(json_response, indent=2, ensure_ascii=False))

    # 请求接口
    REQUEST_URL = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"

    # 配置信息
    appcode = "494cc530c21f42ae96f09239f9270daf"
    img_file = "E:/Proj/NSPrinter/imgs/rec.png"
    params = {
        # 是否需要识别结果中每一行的置信度，默认不需要。 true：需要 false：不需要
        "prob": False,
        # 是否需要单字识别功能，默认不需要。 true：需要 false：不需要
        "charInfo": False,
        # 是否需要自动旋转功能，默认不需要。 true：需要 false：不需要
        "rotate": False,
        # 是否需要表格识别功能，默认不需要。 true：需要 false：不需要
        "table": False,
        # 字块返回顺序，false表示从左往右，从上到下的顺序，true表示从上到下，从左往右的顺序，默认false
        "sortPage": False,
        # 是否需要去除印章功能，默认不需要。true：需要 false：不需要
        "noStamp": False,
        # 是否需要图案检测功能，默认不需要。true：需要 false：不需要
        "figure": True,
        # 是否需要成行返回功能，默认不需要。true：需要 false：不需要
        "row": True,
        # 是否需要分段功能，默认不需要。true：需要 false：不需要
        "paragraph": False,
        # 图片旋转后，是否需要返回原始坐标，默认不需要。true：需要  false：不需要
        "oricoord": True
    }

    request(appcode, img_file, params)
    return


def test_aliyun_handwriting():
    host = 'https://shouxiegen.market.alicloudapi.com'
    path = '/ocrservice/shouxieEng'
    method = 'POST'
    appcode = '494cc530c21f42ae96f09239f9270daf'
    querys = ''
    bodys = {}
    url = host + path

    http = urllib3.PoolManager()
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'APPCODE ' + appcode
    }
    bodys[
        ''] = "{//图像数据：base64编码，要求base64编码后大小不超过4M，最短边至少15px，最长边最大4096px，支持jpg/png/bmp格式，和url参数只能同时存在一个\"img\":\"\",//图像url地址：图片完整URL，URL长度不超过1024字节，URL对应的图片base64编码后大小不超过4M，最短边至少15px，最长边最大4096px，支持jpg/png/bmp格式，和img参数只能同时存在一个\"url\":\"\",//是否需要识别结果中每一行的置信度，默认不需要。true：需要false：不需要\"prob\":false,//是否需要单字识别功能，默认不需要。true：需要false：不需要\"charInfo\":false,//是否需要自动旋转功能，默认不需要。true：需要false：不需要\"rotate\":false,//是否需要表格识别功能，默认不需要。true：需要false：不需要\"table\":false,//字块返回顺序，false表示从左往右，从上到下的顺序，true表示从上到下，从左往右的顺序，默认false\"sortPage\":false}"
    post_data = bodys['']
    response = http.request('POST', url, body=post_data, headers=headers)
    content = response.data.decode('utf-8')
    if (content):
        # print(content)
        json_response = json.loads(content)
        print(json.dumps(json_response, indent=2, ensure_ascii=False))



def main():
    test_aliyun_handwriting()
    print('Hello World')


if __name__ == '__main__':
    main()
