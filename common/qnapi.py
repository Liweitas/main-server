# qnapi.py

import requests
import json




def send_post_request(url, params):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',    
    }

    #response = requests.post('http://192.168.0.121:3030/SaiNiuApi/Call?&post=GetNewNews&data={}', headers=headers, verify=False)
    try:
        response = requests.post(url+"?"+params, headers=headers, verify=False)
    #print(response.text)
        return response
    except Exception as e:
        print(e)
        return None

def send_postfunction_request(url,postname,payload):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    #print(url,postname,payload)
    data = 'data='+str(payload).replace('\'','"')
    #print(data)
    data =data.encode()
    try:
        response = requests.post(url+'?&post='+postname, headers=headers, data=data)
        return response
    except Exception as e:
        print(e)
        return None

    

def process_response(response):
    """
    处理接口响应
    :param response: 接口返回的 JSON 数据
    :return: 提取的信息或错误处理
    """
    try:
        if response.get("code") == 200:  # 检查响应码是否为成功
            msg = response.get("msg", "No message provided")
            data = response.get("data", "No data provided")
            passkey = response.get("passkey", "No passkey provided")
            return {"msg": msg, "data": data, "passkey": passkey}
        elif response.get("code") == 501:  # 处理 501 错误
            msg = response.get("msg", "No message provided")
            passkey = response.get("passkey", "No passkey provided")
            return {"error": msg, "passkey": passkey}
        else:
            return {"error": response.get("msg", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}