import json
import sqlite3


# 函数1: 解析 JSON 数据
def parse_response(response):
    """
    解析返回的 JSON 数据。
    
    :param response: 返回的 JSON 数据（字典形式）
    :return: 解析后的字典数据，如果解析失败返回 None
    """
    try:
        json_response = json.loads(response)
        # print("JSON response:", json_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        json_response = None
    if json_response.get("code") == 200 and json_response.get("msg") == "调用成功":
        try:
            data = json.loads(json_response["data"])  # 解析嵌套的 JSON 数据
            data["passkey"] = json_response["passkey"]  # 添加 passkey 字段
            return data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing data: {e}")
            return None
    else:
        # print("Response indicates failure.")
        print("  没有新消息")
        return None


def extract_group_info(json_data):
    """
    解析 JSON 数据并提取 groupName 和 groupId。
    :param json_data: str, JSON 格式的字符串
    :return: list, 包含 (groupName, groupId) 的元组列表
    """
    try:
        data = json.loads(json_data)
        groups = []

        if "data" in data and "result" in data["data"]:
            result = json.loads(data["data"]["result"])
            if "module" in result:
                for group in result["module"]:
                    group_name = group.get("groupName", "Unknown")
                    group_id = group.get("id", None)
                    if group_id is not None:
                        groups.append((group_name, group_id))

        return groups
    except json.JSONDecodeError:
        print("JSON 解析错误")
        return []


def get_group_id_by_name(json_data, target_group_name):
    """
    根据 groupName 查找对应的 groupId。
    :param json_data: str, JSON 格式的字符串
    :param target_group_name: str, 目标分组名称
    :return: int or None, groupId 或 None（未找到）
    """
    groups = extract_group_info(json_data)
    for name, group_id in groups:
        # if name == target_group_name:
        if target_group_name in name:
            return group_id
    return None  # 如果未找到，返回 None


def get_customer_service_group_ids(json_data, target_group_name):
    """
    从 JSON 数据中提取包含 '客服分组' 关键词的 groupName 对应的 id。
    :param json_data: str, JSON 格式的字符串
    :return: list, 满足条件的 groupId 列表
    """
    try:
        data = json.loads(json_data)
        result_str = data.get("data", {}).get("result", "{}")
        result = json.loads(result_str)  # 解析嵌套 JSON

        group_ids = []
        if "module" in result:
            for group in result["module"]:
                group_name = group.get("groupName", "")
                group_id = group.get("id", None)
                if target_group_name in group_name and group_id is not None:
                    group_ids.append(group_id)

        return group_ids
    except json.JSONDecodeError:
        print("JSON 解析错误")
        return []


# 函数2: 保存数据到 SQLite
def save_to_database(data, db_name="messages.db"):
    """
    将解析后的数据保存到 SQLite 数据库。
    
    :param data: 解析后的字典数据
    :param db_name: 数据库文件名
    """
    if data is None:
        print("No data to save.")
        return

    try:
        # 连接数据库
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 创建表（如果尚未存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS message (
            loginNick TEXT,
            type TEXT,
            templateId INTEGER,
            cid TEXT,
            messageId TEXT,
            buyerUid TEXT,
            sellerId TEXT,
            time INTEGER,
            message TEXT,
            passkey TEXT
        )
        """)

        # 插入数据
        cursor.execute("""
        INSERT INTO message (loginNick, type, templateId, cid, messageId, buyerUid, sellerId, time, message, passkey)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("loginNick"),
            data.get("type"),
            data.get("templateId"),
            data.get("cid"),
            data.get("messageId"),
            data.get("buyerUid"),
            data.get("sellerId"),
            int(data.get("time", 0)),
            data.get("message"),
            data.get("passkey")
        ))

        # 提交更改
        conn.commit()
        print("Data saved successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        # 关闭连接
        conn.close()

