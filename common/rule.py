import re
from config import QN_TRANS_MESSAGE, logger


# 表情过滤
def emj_check(msg):
    if msg:
        if msg[0:2] == '/:' and len(msg) < 6:
            return msg
    else:
        return None


class DiFyRuleC(object):
    def __init__(self):
        self.filter_info = ['您发送的消息中可能包含了存在交易风险的外部网站或移动互联网应用信息，请勿使用阿里旺旺、千牛以外的其它聊天工具，以确保买卖方沟通、交易安全']

    # 去重：Deduplication
    # 全新0064000230B是有货的。全新0064000230B是有货的。全新0064000230B是有货的。
    @staticmethod
    def deduplication(input_string):
        # 将输入文本按句号“。”分割成子句
        if input_string:
            text_parts = input_string.split("。")
            # 用于记录已出现的子句
            seen = set()
            # 用于存储去重后的文本
            unique_text = []
            # 遍历每个子句
            if len(text_parts) > 1:
                for part in text_parts:
                    if part and part not in seen:  # 如果子句不为空并且是首次出现
                        unique_text.append(part)
                        seen.add(part)
                # 将去重后的子句重新合并为字符串
                input_string = "。".join(unique_text) + "。"

        return input_string

    # 乱码处理
    @staticmethod
    def data_lm(input_string, rule):
        input_string = str(input_string).replace(' ', '')
        rule = rule.replace(' ', '')
        if input_string.find(rule) != -1:
            return 1, QN_TRANS_MESSAGE
        return 0, input_string

    @staticmethod
    def url_check(text):
        try:
            # 正则表达式，用于提取所有 URL
            pattern = r'https?://[^\s\]]+'
            # 使用 re.findall 提取所有链接
            links = re.findall(pattern, text)
            if len(links) > 1:
                text = text.replace(f'，[{links[1]}]', '')
            return 0, text
        except Exception as e:
            logger.error(f'异常错误：{e}')
            return 1, ''

    @staticmethod
    def replace_t(text, dict_={}):
        return text.replace(list(dict_.keys())[0], list(dict_.values())[0])

    @staticmethod
    def r_strip_t(my_string, tag):
        print(my_string, type(my_string))
        return my_string.rstrip(tag)

    @staticmethod
    def di_fy_data_cleaning(msg):
        new_msg = ''
        if msg.find("Answer：)") != -1:
            new_msg = msg
        elif msg.find("Answer：") != -1:
            new_msg = msg
        elif msg.find("Answer:") != -1:
            new_msg = msg
        elif msg.find("Answer:)") != -1:
            new_msg = msg
        elif msg.find("Answer") != -1:
            new_msg = msg
        return new_msg

    @staticmethod
    def remove_taobao_url_in_parentheses(text):
        # 查找第一个左括号和右括号的位置
        start_bracket = text.find('[')
        end_bracket = text.find(']')

        # 查找后面要删除的部分
        remove_start = text.find('(', end_bracket)

        # 如果找到了要保留的部分和要删除的部分
        if start_bracket != -1 and end_bracket != -1 and remove_start != -1:
            # 提取前半部分和链接
            result = text[:remove_start].strip()
            return result
        else:
            return text

    def filter_data(self, msg):
        if msg in self.filter_info:
            return 'continue'
        else:
            return msg


class OcrRuleC(object):
    def __init__(self):
        pass


class YoloRuleC(object):
    def __init__(self):
        pass

    @staticmethod
    def data_cleaning(data):
        # 去除字符串前后空格
        data = data.strip().replace(" ", '')
        # 去除特殊字符，只保留字母、数字和空格
        data = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', data)
        return data

    @staticmethod
    def th_rule(data):
        # 替换规则
        if data == "DZ90X10":
            return "DZ90X1D"
        elif data == "ASE520":
            return "ASE52U"
        elif data == "B90M2SU1":
            return "E90M2SU1"
        elif data == "MXA9C":
            return "FMXA9C"
        elif data == "DZ90X18":
            return "DZ90X1B"
        elif data == "EOOCY1":
            return "L100CY1"
        elif data == "L1OOCY1":
            return "L100CY1"
        elif data == "DZ1OOV1Z":
            return "DZ100V1Z"
        elif data == "DZ120V10":
            return "DZ120V1D"
        elif data == "A120CY":
            return "A120CY1"
        elif data == "CHMO9OTV":
            return "CHM090TV"
        elif data == "NTB1113Y":
            return "VTB1113Y"
        elif data == "TIANyIN":
            return "TIANYIN"
        elif data == "PA99HME":
            return "PA99HMF"
        elif data == "Th1116Y":
            return "TH1116Y"
        elif data == "SZ110H18":
            return "SZ110H1H"
        elif data == "QD59L":
            return "QD59U"
        elif data == "VFK79C":
            return "VEK79C"
        elif data == "DZ120V18":
            return "DZ120V1B"
        elif data == "QD75HHP":
            return "QD75H"
        elif data == "VFA090CY!":
            return "VFA090CY1"
        elif data == "ASK103053UFZ":
            return "ASK103D53UFZ"
        elif data == "DLA5985X0EA":
            return "DLA5985XOEA"
        elif data == "LU76gY":
            return "LU76CY"
        elif data == "PZ130H1E":
            return "PZ130H1Z"
        elif data == "DZ100V10":
            return "DZ100V1C"
        elif data == "HVM90MS":
            return "HVM90MS a"
        elif data == "VELO90CY7":
            return "VELO90CY1"
        elif data == "HVD90MT":
            return "HVD90MT a"
        elif data == "VETZ11OL":
            return "VETZ110L"
        return data
