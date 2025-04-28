# qnapi-helper.py
import aiohttp
import logging
from common.qnapi import send_post_request, process_response, send_postfunction_request
from common.parse import parse_response
from config import QN_URL
from config import logger
base_url = QN_URL

async def async_httpcall(url, postname, data):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = 'data='+str(data).replace('\'','"')
    data =data.encode()
    async with aiohttp.ClientSession() as session:
        async with session.post(url + '?&post=' + postname,headers=headers, data=data) as response:
            return await response.text()

def httpcall(postname, data, is_async=False):
    url = base_url + "/SaiNiuApi/Call"
    data = {}

    if is_async:
        
        return async_httpcall(url, postname, data)
    else:
        response = send_postfunction_request(url, postname, data)
        return response.text

async def async_functioncall(postname, data):
    url = base_url + "/SaiNiuApi/Function"
    #headers = {
    #    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #    'Accept-Language': 'zh-CN,zh;q=0.9',
    #    'Connection': 'keep-alive',
    #    'Upgrade-Insecure-Requests': '1',
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',    
    
    #}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = 'data='+str(data).replace('\'','"')
    data = data.encode()
    async with aiohttp.ClientSession() as session:
        async with session.post(url + '?&post=' + postname, headers=headers, data=data) as response:
            logging.info(response)
            return await response.text()

def functioncall(postname, data, is_async=False):
    url = base_url + "/SaiNiuApi/Function"
    if is_async:
        return async_functioncall(postname, data)
    else:
        response = send_postfunction_request(url, postname, data)
        return response.text
    
def apicall(postname, data, is_async=False):
    url = base_url + "/SaiNiuApi/Api"
    if is_async:
        return async_functioncall(postname, data)
    else:
        response = send_postfunction_request(url, postname, data)
        return response.text

