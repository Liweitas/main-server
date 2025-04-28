import re
import os
import uuid
import time
import redis
import json
import config
import pandas as pd
from common import rule
from collections import defaultdict
from common import global_variable
from datetime import datetime


def parse_datetime(date_str, formats=None):
    """解析时间字符串"""
    formats = formats or ["%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间格式: {date_str}")


def calculate_time_difference(time1, time2):
    """计算时间差（秒）"""
    timestamp1 = time1.timestamp()
    timestamp2 = time2.timestamp()
    return abs(timestamp1 - timestamp2)


class ExpiringArray:
    def __init__(self):
        self.data = {}

    def add(self, username, item, expire_time):
        # expire_time 是相对于当前时间的过期秒数
        self.data[username] = (item, time.time() + expire_time)  # 直接覆盖之前的值

    def get_valid_items(self, username=None):
        current_time = time.time()
        if username:
            # 如果提供了username，检查该用户的有效项
            item_data = self.data.get(username)
            if item_data and item_data[1] > current_time:  # 检查是否未过期
                return item_data[0]  # 返回该用户的项
            return None  # 用户不存在或已过期
        else:
            # 如果没有提供username，返回所有有效项
            valid_items = {username: (item, expire) for username, (item, expire) in self.data.items() if
                           expire > current_time}
            return valid_items if valid_items else None  # 如果没有有效项，则返回 None

    def clear_expired(self):
        current_time = time.time()
        expired_users = [username for username, (item, expire) in self.data.items() if expire <= current_time]
        for username in expired_users:
            del self.data[username]


# 产品库存检测
def product_check(product, producttype):
    try:
        return_res = ''
        # DZ120V1D;BCD-452WSPZM，Refrigerator nameplate;Refrigerator nameplate
        matches_res_l = []
        pd_obj = pd.read_excel(f'{config.file_path}/产品型号.xlsx')
        product_r = pd_obj['产品型号'].tolist()
        avaliable_num = pd_obj['库存数量'].tolist()
        product_type = pd_obj['产品类型'].tolist()
        # 组织数据结构
        product_dict = defaultdict(lambda: [[], []])
        for p_type, p_model, stock in zip(product_type, product_r, avaliable_num):
            new_p_type = global_variable.en_translation_dict.get(p_type)
            if new_p_type == "Mainboard_main board":
                for p_type_m in new_p_type.split("_"):
                    product_dict[p_type_m][0].append(p_model)  # 添加产品型号
                    product_dict[p_type_m][1].append(stock)  # 添加库存数量
            else:
                product_dict[new_p_type][0].append(p_model)  # 添加产品型号
                product_dict[new_p_type][1].append(stock)  # 添加库存数量

        # 转换为普通字典并打印
        res_zw = '图片%s[%s:%s]'
        product_dict = dict(product_dict)
        # 根据类型获取型号
        new_producttype_l = producttype.split(";")
        new_product_l = product.split(";")
        for index_p, new_producttype in enumerate(new_producttype_l):
            res_dict = product_dict.get(new_producttype)
            product = new_product_l[index_p]
            cleaned_data_res_l = product.replace(" ", '').split('&&')
            tag = True
            if res_dict:
                for res in cleaned_data_res_l:
                    ylrc = rule.YoloRuleC()
                    print('清洗前:', res)
                    res = ylrc.data_cleaning(res)
                    res = ylrc.th_rule(res)
                    print('结果返回:', res)
                    res = str(res).upper()
                    print('清洗后', res)
                    # 先做模糊匹配，如果匹配不到
                    product_l = res_dict[0]
                    for index, pro in enumerate(product_l):
                        if pro == res and pro not in matches_res_l:
                            tag = False
                            return_res = return_res + res_zw % (index_p + 1, new_producttype, pro) + ','
                            break
                    if not tag:
                        break
                if tag:
                    return_res = return_res + res_zw % (index_p + 1, new_producttype, '图片不清楚') + ','
            else:
                if new_producttype == "Refrigerator nameplate":
                    return_res = return_res + res_zw % (index_p + 1, new_producttype, product) + ','
        new_res = return_res.rstrip(",")
        if "无型号" in new_res:
            new_res = ""

    except Exception as e:
        new_res = ""
        print('异常错误：', e)
    return new_res


def is_url(text):
    # URL 正则表达式（简单版）
    urls = re.findall(r'https?://\S+', text)
    return True if urls else False


# url检测
def extract_id(url):
    # 检查 URL 是否有效
    if not is_url(url):
        return "无效的 URL"
    # 提取 URL 中的 id 参数
    match = re.search(r'[?&]id=(\d+)', url)
    if match:
        return match.group(1)


class RedisConnClass(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=16379, db=0)

    # 如果转人工存在，则不进行转人工内容输出
    def w_redis(self, key, value, expiration_time=200):
        # 连接到本地的 Redis 实例
        self.r.setex(key, expiration_time, value)

    def get_redis(self, key):
        return self.r.get(key)

        # 向 Redis Set 添加值（会自动去重）

    def sadd_redis(self, key, *values):
        """向集合 (Set) 添加一个或多个值"""
        return self.r.sadd(key, *values)

    # **新增：获取 Redis Set 的所有成员**
    def smembers_redis(self, key):
        """获取集合 (Set) 中的所有值"""
        return self.r.smembers(key)

    # **新增：删除 Redis Set 中的某个成员**
    def srem_redis(self, key, value):
        """从集合 (Set) 中移除指定值"""
        return self.r.srem(key, value)

        # 向 Redis List 添加元素（右端插入）

    def rpush_redis(self, key, *values):
        """将一个或多个值添加到列表（右端）"""
        return self.r.rpush(key, *values)

        # 获取 Redis List 中的元素（从左到右，指定范围）

    def lrange_redis(self, key, start=0, end=-1):
        """获取列表中的所有元素（默认为所有元素）"""
        return self.r.lrange(key, start, end)


# 同字典数据合并
def num_(data):
    # 将列表转换为 DataFrame
    df = pd.DataFrame(data)
    # 对 DataFrame 进行求和操作（按列汇总）
    result = df.sum()
    # 输出结果
    result_dict_list = [{key: value} for key, value in result.items()]
    return result_dict_list


# 获取当前时间
def get_data():
    # 获取当前的 datetime 对象
    now = datetime.now()
    # 转换为日期格式
    return now.date()


# 获取uuid：
def get_uuid():
    return uuid.uuid4()


# 转接数据记录
class InfoDataUuid(object):
    def __init__(self, **kwargs):
        ck_d = kwargs.get('ck_d', {})
        self.zj_dict = {
            'userNick': kwargs.get('userNick'),
            'buyerUid': kwargs.get('buyerNick'),
            'message': kwargs.get('message'),
            'answer': kwargs.get('answer'),
            'humman': kwargs.get('humman'),
            'source_photo_path': ck_d.get('source_photo_path'),
            'error_photo_path': ck_d.get('error_photo_path'),
            'pec_photo_path': ck_d.get('pec_photo_path'),
            'producttype': ck_d.get('producttype'),
            'text_res_s': ck_d.get('text_res_s'),
        }
        self.json_data_save_path = ''

    @staticmethod
    def write_json(path, dict_, l_d_d):
        try:
            data_s = str(get_data())
            if l_d_d:
                l_inner_l = l_d_d.get(data_s)
                if l_inner_l:
                    l_inner_l.append(dict_)
                else:
                    l_d_d = {}
                    l_d_d[data_s] = [dict_]
            else:
                l_d_d = {data_s: [dict_]}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(l_d_d, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

    @staticmethod
    def read_json(path_):
        try:
            with open(path_, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return 'error'

    @staticmethod
    def return_path():
        path_s = f'{global_variable.FILE_PATH}/transfer_record.json'
        path_c = f'{global_variable.FILE_PATH_C}/transfer_record.json'
        if os.path.exists(path_c):
            path = path_c
        elif os.path.exists(path_s):
            path = path_s
        else:
            path = path_s
            with open(path, "w", encoding="utf-8") as f:
                pass
        return path
