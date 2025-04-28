import os
from datetime import datetime
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
import time

# 配置加载（可通过环境变量或默认值）
BASE_URL = os.getenv("BASE_URL", "http://192.168.1.27/v1")
APP_KEY = os.getenv("APP_KEY", "app-v24MvgIYxbWo882YRUlJuMjc")
DIFY_MODE = os.getenv("DIFY_MODE", "streaming")
QN_URL = os.getenv("QN_URL", "http://192.168.1.128:3030")
QN_TRANS_MODE = "Group"
QN_GROUP = "客服分组"
QN_CS = "wsy"
QN_TRANS_MESSAGE = "亲爱的，稍等给您转专席客服"

# 日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """自定义的每日日志处理器，确保每天使用新文件"""

    def __init__(self, filename, encoding):
        # 生成带日期的文件名
        self.base_filename = filename
        self.date_str = time.strftime("%Y-%m-%d")
        actual_filename = f"{filename}_{self.date_str}.log"  # 添加.log后缀

        super().__init__(
            filename=actual_filename,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding=encoding,
            delay=False
        )

    def emit(self, record):
        """重写emit方法，确保每条日志立即写入"""
        try:
            if self.stream is None:
                self.stream = self._open()
            StreamHandler.emit(self, record)
            self.flush()  # 立即刷新缓冲区
            if self.stream is not None:
                self.stream.flush()  # 确保写入底层文件
        except Exception:
            self.handleError(record)

    def rotation_filename(self, default_name):
        """重写文件名生成方法"""
        return self.baseFilename

    def getFilesToDelete(self):
        """获取要删除的旧文件"""
        dir_name, base_name = os.path.split(self.base_filename)
        file_names = os.listdir(dir_name) if dir_name else os.listdir('.')
        result = []
        prefix = base_name + "."

        for fileName in file_names:
            if fileName.startswith(prefix):
                suffix = fileName[len(prefix):]
                if self.extMatch.match(suffix.replace('.log', '')):  # 移除.log后缀再匹配
                    result.append(os.path.join(dir_name, fileName))

        result.sort()
        if len(result) < self.backupCount:
            return []
        else:
            return result[:len(result) - self.backupCount]


def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 设置日志文件基础路径
    log_base = os.path.join(LOG_DIR, 'qnapi')

    # 创建自定义的日志处理器
    file_handler = DailyRotatingFileHandler(
        filename=log_base,
        encoding='utf-8'
    )

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 清除现有的处理器
    logger.handlers.clear()

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 设置不传播到父记录器
    logger.propagate = False

    return logger


# 创建logger实例
logger = setup_logging()
base_path = os.path.dirname(os.path.abspath(__file__))
file_path = f'{base_path}/files'
q_file_path = f'{base_path}/files/cache_dict.pkl'
CACHE_DURATION = 20
