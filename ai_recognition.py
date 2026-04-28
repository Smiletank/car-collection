import base64
from zhipuai import ZhipuAI
import os

def encode_image(image_path):
    """将图片编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def recognize_cars(image_path, api_key):
    """
    调用智谱GLM-4V识别图片中的小车
    
    返回格式：
    [
        {"brand": "风火轮", "model": "保时捷911", "color": "红色", "note": "", "series": "", "code": ""},
        {"brand": "火柴盒", "model": "野马", "color": "蓝色", "note": "", "series": "", "code": ""}
    ]
    """
    client = ZhipuAI(api_key=api_key)
    
    # 编码图片
    image_base64 = encode_image(image_path)
    image_url = f"data:image/jpeg;base64,{image_base64}"
    
    prompt = """
你是一个1:64合金小车收藏专家。请仔细识别这张图片中的所有合金小车模型。

对于每一辆小车，请识别以下信息：
- brand: 品牌（如：风火轮/Hot Wheels、火柴盒/Matchbox、TLV、多美卡/Tomica、其他）
- model: 车型名称（如：保时捷911、福特野马、日产GT-R等，尽量识别具体型号）
- color: 颜色或涂装描述
- series: 系列（如：Super Truck、Mainline、Car Culture等，如果能看到底盘信息）
- code: 编号（底盘上的编号，如1186、JJHE2等）
- note: 其他备注（如特殊版本、联名款、年份等）

请以JSON数组格式返回，不要包含其他解释文字。格式如下：
[
    {"brand": "品牌", "model": "车型", "color": "颜色", "series": "系列", "code": "编号", "note": "备注"},
    ...
]

如果无法识别某辆车的某个字段，请填写"未知"。
请尽量识别出具体车型名称，不要只写品牌名。
"""

    response = client.chat.completions.create(
        model="glm-4v-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
    )
    
    result_text = response.choices[0].message.content
    
    # 解析JSON结果
    import json
    import re
    
    # 提取JSON部分（去除markdown代码块标记）
    json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group())
    else:
        result = json.loads(result_text)
    
    return result


def recognize_with_bottom(front_path, bottom_path, api_key):
    """
    结合正面图和底盘图识别，获取更详细信息
    
    返回格式：
    [
        {"brand": "风火轮", "model": "Ford F150 Lightning", "color": "深蓝色", "series": "Super Truck", "code": "1186", "note": ""}
    ]
    """
    client = ZhipuAI(api_key=api_key)
    
    # 编码两张图片
    front_base64 = encode_image(front_path)
    bottom_base64 = encode_image(bottom_path)
    
    prompt = """
你是一个1:64合金小车收藏专家。现在有两张图片：正面展示图和底盘特写图。

请结合两张图片的信息，识别这辆小车的详细信息：

从底盘图中提取：
- 具体车型名称（如 Ford F150 Lightning）
- 系列名称（如 Super Truck）
- 编号（如 1186, JJHE2）
- 生产年份（如 ©2026）

从正面图中提取：
- 颜色和涂装
- 特殊装饰或拉花

请返回JSON格式：
[
    {"brand": "品牌", "model": "具体车型名称", "color": "颜色涂装", "series": "系列", "code": "编号", "note": "其他备注"}
]

确保车型名称是具体的型号，不要只写品牌名。
"""

    response = client.chat.completions.create(
        model="glm-4v-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{front_base64}"}
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{bottom_base64}"}
                    }
                ]
            }
        ],
    )
    
    result_text = response.choices[0].message.content
    
    # 解析JSON结果
    import json
    import re
    
    json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group())
    else:
        result = json.loads(result_text)
    
    return result


def search_car_info(brand, model, api_key):
    """
    根据品牌和车型搜索详细信息
    
    返回：{"series": "系列", "code": "编号", "note": "备注"}
    """
    client = ZhipuAI(api_key=api_key)
    
    prompt = f"""
请帮我查找风火轮/火柴盒小车的信息：

品牌：{brand}
车型：{model}

请告诉我：
1. 这款车属于哪个系列？（如：Mainline、Super Truck、Car Culture等）
2. 编号是多少？
3. 有什么特殊信息？（年份、限量、联名等）

如果找不到精确信息，请根据品牌和车型推测可能的信息。
请以JSON格式返回：
{{"series": "系列", "code": "编号", "note": "备注"}}
"""

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    import json
    import re
    
    result_text = response.choices[0].message.content
    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
    
    if json_match:
        return json.loads(json_match.group())
    return {"series": "", "code": "", "note": ""}


def recognize_and_enrich(image_path, api_key):
    """
    识别图片并自动补全信息
    """
    # 先识别图片
    cars = recognize_cars(image_path, api_key)
    
    # 对每辆车补全信息
    for car in cars:
        if car.get('model') and car['model'] != '未知':
            extra_info = search_car_info(car['brand'], car['model'], api_key)
            # 只补全空缺的字段
            if not car.get('series'):
                car['series'] = extra_info.get('series', '')
            if not car.get('code'):
                car['code'] = extra_info.get('code', '')
            if not car.get('note'):
                car['note'] = extra_info.get('note', '')
    
    return cars