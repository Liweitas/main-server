import os

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 是否处理辅助空
AUX_OFF_ON = True
FILE_PATH = f"{base_path}/files"
TMP_PATH = f"{base_path}/tmp"
# 原图存储路径
SOURCE_IMAGE_SAVE_PATH = '/home/taoseekai/wim/storge_server/photo/source_photo'
# 检测后的图片
RECOGNIZE_PHOTO = '/home/taoseekai/wim/storge_server/photo/recognize_photo'

ERROR_IMAGE_SAVE_PATH = '/home/taoseekai/wim/storge_server/photo/check_error'

FILE_PATH_C = '/home/taoseekai/wim/storge_server/files'

SERVER_IP = 'http://192.168.1.27:8001'

en_translation_dict = {
    "冰箱": "Refrigerator",
    "冰箱门": "Refrigerator Door",
    "压缩机": "Compressor",
    "变频板": "Inverter Board",
    "小绿板": "Small Green Board",
    "快递单": "Express Bill / Delivery Note",
    "排水泵": "Drain Pump",
    "显示板": "Display Panel",
    "洗衣机": "Washing Machine",
    "风机": "Fan",
    "风": "Air Damper",
    "主板": "Mainboard_main board"
}
cn_translation_dict = {
    "Refrigerator": "冰箱",
    "Refrigerator Door": "冰箱门",
    "Compressor": "压缩机",
    "Inverter Board": "变频板",
    "Small Green Board": "小绿板",
    "Express Bill / Delivery Note": "快递单",
    "Drain Pump": "排水泵",
    "Display Panel": "显示板",
    "Washing Machine": "洗衣机",
    "Fan": "风机",
    "Air Damper": "风",
    "Main Board": "主板"

}
