import sys
import importlib
import asyncio
from common import rule
from common import utils
from common.utils import ExpiringArray
from common.rule import DiFyRuleC
from config import QN_CS, QN_GROUP, DIFY_MODE, QN_TRANS_MODE
from common.qnapi_helper import httpcall, parse_response, functioncall, apicall
from common.parse import parse_response, get_group_id_by_name
from config import logger
from config import QN_TRANS_MESSAGE
from common.api_helper import APIHelper
text_cache = {} 


async def check_new_info():
    while True:
        try:
            logger.info("开始检查新消息")
            response = await httpcall("GetNewNews", "{}", is_async=True)
            data = parse_response(response)
            if data:
                logger.info(f"收到新消息: {data}")
                await preprocess_info(data)
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"检查新消息时出错: {str(e)}", exc_info=True)

# 处理文本
async def handle_text_message(message, user_id, nicker, buyerUid, file_ids=[],cache_key=""):
    dfr_ = rule.DiFyRuleC()
    ck_d = text_cache[cache_key]
    if message == "":
        message = "这个"
    nicker = str(nicker)
    user_id = str(user_id)
    logger.info([message, user_id, nicker, file_ids])
    api_helper = APIHelper()
    conversation_id = conversation_ids.get_valid_items(user_id + "_" + nicker)
    inputs = {"userNick": nicker}
    res_list = nicker.split(':')
    userNick = res_list[0] if res_list else ''
    inputs.update(userNick=userNick)
    # 链接处理
    if not message:
        pass
    else:
        if utils.is_url(message):
            message = f'咨询这个链接[{message}]'
    print('信息返回:', message)
    logger.info(ck_d)
    # dify识别
    inputs.update(buyerEid=ck_d['loginId'])
    dify_data = {}

    try:
        print("请求调用！")
        dify_data = api_helper.send_chat_message(f'{message}', user_id,
                                                inputs=inputs,
                                                file_ids=[],
                                                conversation_id=conversation_id, response_mode=DIFY_MODE)
        logger.info(dify_data)
        conversation_id = dify_data['conversation_id']
        conversation_ids.add(user_id + "_" + nicker, str(conversation_id), 600)
        answer = dify_data["answer"]
        print(answer, "返回答案")
    except Exception as e:
        answer = ""
        logger.error(e)
    if not answer == "人工":
        di_fy_rl = DiFyRuleC()
        # 去重
        answer = di_fy_rl.deduplication(answer)
        # 特殊字符替换
        if utils.is_url(answer):
            answer = di_fy_rl.replace_t(answer, {'&': '%26'})
        if answer.endswith("\n。"):
            answer = di_fy_rl.r_strip_t(answer, '\n。')
        # 乱码处理
        humman, answer = di_fy_rl.data_lm(answer, 'query = ')
        humman, answer = di_fy_rl.url_check(answer)


    if answer == "" or answer == None:
        answer = QN_TRANS_MESSAGE
        humman = 1

    if "转人工" in answer or "AI" in answer or "转接人工" in answer:
        answer = QN_TRANS_MESSAGE
        humman = 1

    answer = answer.replace('"', '')
    # 检测
    params = {
        'userNick': nicker.encode("gbk").decode("gbk"),
        'buyerNick': user_id,
        'text': answer,
        'siteid': 'cntaobao',
        'waitingTime': 3000
    }
    # 转客服时记录
    logger.info(params)
    trans = {}
    # 如果redis没有数据时，可转接。
    print("赛牛调用")
    senddata = functioncall('SendMessages', params)
    print("赛牛回调")
    logger.info(senddata)
    if user_id == "t_1514353800520_0314":
        return None
    if humman == 1:
        if QN_TRANS_MODE == "Group":
            trans['userNick'] = nicker
            groupdata = apicall('GetReceptionGroup', trans)
            groupid = get_group_id_by_name(groupdata, QN_GROUP)
            trans['buyerUid'] = buyerUid
            trans['groupId'] = groupid
            trans['reason'] = '智能体希望转人工客服'
            senddata = await functioncall('TransferBuyerToGroups', trans, is_async=True)
        else:
            trans['userNick'] = nicker
            trans['buyerNick'] = user_id
            trans['toNick'] = trans['toNick'] = nicker.split(':')[0] + ":" + QN_CS
            senddata = await functioncall('TransferBuyerNick', trans, is_async=True)
            logger.info(trans)
            logger.info(senddata)

# 信息缓存
async def preprocess_info(data):
    """ 预处理信息，将未处理的文本信息合并，下载和上传图片信息 """
    if "转交给" in data['message']:
        return None
    message_type = data['type']
    user_id = data['buyerNick']
    buyerUid = data['buyerUid']
    store_name = data['loginNick']
    loginId = data['loginId']
    print('接到的用户loginId：', loginId)
    logger.debug(data)
    # 使用用户ID和店铺名作为缓存的键
    cache_key = (user_id, store_name)
    # 接待人数
    if cache_key not in text_cache:
        text_cache[cache_key] = {
            'message': '',
            'fileids': [],
            'local_path': None,
            'buyerNick': data['buyerNick'],
            'buyerUid': data['buyerUid'],
            'userNick': data['loginNick'],
            'loginId': data['loginId'],
            'time': None,
        }
    if message_type == '文本消息':
        # 合并文本信息
        current_message = text_cache[cache_key].get('message', '')
        new_message = data['message']
        combined_message = f"{current_message}\n{new_message}".strip()
        text_cache[cache_key]['message'] = combined_message

# 信息处理
async def process_info():
    while True:
        try:
            # 创建需要处理的缓存键的副本，避免处理过程中的字典修改问题
            cache_keys = list(set(text_cache.keys()))
            for cache_key in cache_keys:
                try:
                    user_id, store_name = cache_key
                    if cache_key not in text_cache:
                        continue
                    cache_data = text_cache[cache_key]
                    # 获取所有需要的数据
                    combined_message = cache_data.get('message', '')
                    file_ids = cache_data.get('fileids', [])
                    nicker = cache_data.get('userNick')
                    buyernick = cache_data.get('buyerNick')
                    buyerUid = cache_data.get('buyerUid')
                    # 检查必要的字段是否存在
                    if not all([nicker, buyernick, buyerUid]):
                        logger.error(f"Missing required fields for cache_key {cache_key}")
                        continue
                    # 只有在确认消息发送成功后才清空缓存
                    if combined_message or file_ids:
                        try:
                            if len(file_ids) > 5:
                                for i in range(0, len(file_ids), 5):
                                    await handle_text_message(
                                        combined_message,
                                        buyernick,
                                        nicker,
                                        buyerUid,
                                        file_ids[i:i + 5],
                                        cache_key
                                    )
                            else:
                                await handle_text_message(
                                    combined_message,
                                    buyernick,
                                    nicker,
                                    buyerUid,
                                    file_ids,
                                    cache_key
                                )
                            if cache_key in text_cache:
                                text_cache[cache_key]['message'] = ''
                                text_cache[cache_key]['fileids'] = []

                        except Exception as e:
                            logger.error(f"Error processing message for {cache_key}: {str(e)}")
                            # 消息处理失败，保留在缓存中
                            continue


                except Exception as e:
                    logger.error(f"Error processing cache_key {cache_key}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error in process_info main loop: {str(e)}")

        await asyncio.sleep(2)  # 每8秒处理一次信息



# 启动
async def main():
    global conversation_ids
    conversation_ids = ExpiringArray()
    task1 = asyncio.create_task(check_new_info())
    task2 = asyncio.create_task(process_info())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    logger.info("启动服务")
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            logger.info("开始运行服务")
            asyncio.run(main())
        elif sys.argv[1] == 'stop':
            logger.info("停止服务")
            sys.exit()
        elif sys.argv[1] == 'reload':
            logger.info("重新加载配置")
            importlib.reload(importlib.import_module('config'))
            # 重新加载后需要重新设置logger
            from config import logger

            logger.info("配置重新加载完成")
            sys.exit()
    else:
        try:
            logger.info("开始运行服务")
            asyncio.run(main())
        except Exception as e:
            logger.error(f"服务运行出错: {str(e)}", exc_info=True)
