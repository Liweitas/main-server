import requests
from config import BASE_URL, APP_KEY, logger
import mimetypes
from tenacity import retry, stop_after_attempt, wait_fixed
import aiohttp
import json


class APIHelper:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def upload_file(file_path, user_id):
        """上传文件"""
        url = f"{BASE_URL}/files/upload"
        headers = {"Authorization": f"Bearer {APP_KEY}"}
        mime_type, encoding = mimetypes.guess_type(file_path)
        files = {'file': (file_path, open(file_path, 'rb'), mime_type)}
        data = {'user': user_id}
        try:
            logger.debug(f"正在上传文件到 {url}...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=10)
            response.raise_for_status()
            logger.info(f"文件上传成功: {file_path}")
            return response.json().get("id", None)
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return None

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def send_chat_message(query, user_id, inputs={}, file_ids=[], conversation_id="", response_mode="blocking"):
        """发送聊天消息"""
        url = f"{BASE_URL}/chat-messages"
        headers = {
            "Authorization": f"Bearer {APP_KEY}",
            "Content-Type": "application/json"
        }
        print(f"第一段:{APP_KEY}")
        if len(file_ids) > 0:
            files = []
            for file_id in file_ids:
                files.append({
                    "type": "image",
                    "transfer_method": "local_file",
                    "upload_file_id": file_id
                })
        else:
            files = []
        logger.debug(f"附件信息: {files}")
        payload = {
            "inputs": inputs,
            "query": query,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user_id,
            "files": files
        }
        try:
            logger.info(f"发送消息到 {url}: {payload}")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            content_type = response.headers['Content-Type']
            print(content_type)
            if "text/event-stream;" in content_type:
                response.raise_for_status()
                r = json.loads(parse_sse(response.text))
                print(r)
                return r
            else:
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return None

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def send_chat_messagebyurl(query, user_id, file_urls=[], conversation_id=""):
        """发送聊天消息"""
        url = f"{BASE_URL}/chat-messages"
        headers = {
            "Authorization": f"Bearer {APP_KEY}",
            "Content-Type": "application/json"
        }
        if len(file_urls) > 0:
            files = []
            for file_url in file_urls:
                logger.debug(f"处理文件URL: {file_url}")
                files.append({
                    "type": "image",
                    "transfer_method": "remote_url",
                    "url": file_url
                })
        else:
            files = []
        logger.debug(f"附件信息: {files}")
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "conversation_id": conversation_id,
            "user": user_id,
            "files": files
        }
        try:
            logger.info(f"发送消息到 {url}: {payload}")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return None

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def send_chat_message_async(query, user_id, inputs={}, file_ids=[], conversation_id=""):
        """发送聊天消息"""
        url = f"{BASE_URL}/chat-messages"
        headers = {
            "Authorization": f"Bearer {APP_KEY}",
            "Content-Type": "application/json"
        }
        if len(file_ids) > 0:
            files = []
            for file_id in file_ids:
                files.append({
                    "type": "image",
                    "transfer_method": "local_file",
                    "upload_file_id": file_id
                })
        else:
            files = []
        logger.debug(f"附件信息: {files}")
        payload = {
            "inputs": inputs,
            "query": query,
            "response_mode": "blocking",
            "conversation_id": conversation_id,
            "user": user_id,
            "files": files
        }
        try:
            logger.info(f"异步发送消息到 {url}: {payload}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=60) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"异步发送消息失败: {e}")
            return None


def parse_sse(sse_text):
    answers = []
    conversation_id = None
    message_id = None

    for line in sse_text.splitlines():
        if line.startswith("data: "):
            json_data = line[6:]
            try:
                event_data = json.loads(json_data)
                if "conversation_id" in event_data:
                    conversation_id = event_data["conversation_id"]
                if "message_id" in event_data:
                    message_id = event_data["message_id"]
                if event_data.get("event") == "agent_message" and "answer" in event_data:
                    answers.append(event_data["answer"])
            except json.JSONDecodeError:
                logger.error(f"JSON解析错误: {json_data}")

    return json.dumps({
        "conversation_id": conversation_id,
        "message_id": message_id,
        "answer": "".join(answers)
    }, ensure_ascii=False)
