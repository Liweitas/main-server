import requests
import json
# from qnapi_async import config
from tenacity import retry, stop_after_attempt, wait_fixed

'''
    {
  "orderInfo": {
    "orderId": "4244644335821941414",
    "status": "未完成",
    "afterSaleStatus": "售后中",
    "createTime": "2025-02-25 16:47:25",
    "payTime": "2025-02-25 16:47:50",
    "consignTime": "2025-02-25 17:25:56",
    "endTime": "2025-03-07 17:26:08",
    "orderTotal": "200.00",
    "discount": "10.00",
    "actualPayment": "190.00",
    "logistics": {
      "company": "顺丰速运",
      "trackingNumber": "SF3150561359324",
      "estimatedShippingTime": "2025-02-27 16:47"
    },
    "receiver": {
      "name": "于**",
      "address": "河北省保定市清苑区***********",
      "phone": "***********"
    }
  },
  "items": [
    {
      "itemId": "886994761031",
      "name": "全新东贝定频 R600A 制冷剂冰箱冰柜压缩机 D65CY1 A120CY1 S118CY1",
      "sku": "全新L126CY1（制冷量215W 410-520升用）",
      "quantity": 1,
      "originalPrice": "210.00",
      "discountedPrice": "200.00",
      "promotion": {
        "description": "200-10:省10.00元",
        "discount": "10.00"
      },
      "refundStatus": "请处理换货申请",
      "logisticsStatus": "运输中",
      "imageUrl": "//img.alicdn.com/bao/uploaded/i3/2214143346879/O1CN01wb0Wq020gdZNvVVKe_!!2214143346879.jpg",
      "links": {
        "product": "https://item.taobao.com/item.htm?id=886994761031",
        "snapshot": "https://trade.taobao.com/trade/detail/tradeSnap.htm?snapShot=true&tradeID=4244644335821941414"
      }
    }
  ],
  "actions": {
    "orderDetail": "https://trade.taobao.com/trade/detail/trade_order_detail.htm",
    "viewLogistics": true,
    "requestAfterSale": true,
    "initiateExchange": true,
    "invoice": true,
    "addRemark": true
  }
}

'''
data_ = {
    "orderInfo": {
        "orderId": "4244644335821941414",
        "status": "未完成",
        "afterSaleStatus": "售后中",
        "createTime": "2025-02-25 16:47:25",
        "payTime": "2025-02-25 16:47:50",
        "consignTime": "2025-02-25 17:25:56",
        "endTime": "2025-03-07 17:26:08",
        "orderTotal": "200.00",
        "discount": "10.00",
        "actualPayment": "190.00",
        "logistics": {
            "company": "顺丰速运",
            "trackingNumber": "SF3150561359324",
            "estimatedShippingTime": "2025-02-27 16:47"
        },
        "receiver": {
            "name": "于**",
            "address": "河北省保定市清苑区***********",
            "phone": "***********"
        }
    },
    "items": [
        {
            "itemId": "886994761031",
            "name": "全新东贝定频 R600A 制冷剂冰箱冰柜压缩机 D65CY1 A120CY1 S118CY1",
            "sku": "全新L126CY1（制冷量215W 410-520升用）",
            "quantity": 1,
            "originalPrice": "210.00",
            "discountedPrice": "200.00",
            "promotion": {
                "description": "200-10:省10.00元",
                "discount": "10.00"
            },
            "refundStatus": "请处理换货申请",
            "logisticsStatus": "运输中",
            "imageUrl": "//img.alicdn.com/bao/uploaded/i3/2214143346879/O1CN01wb0Wq020gdZNvVVKe_!!2214143346879.jpg",
            "links": {
                "product": "https://item.taobao.com/item.htm?id=886994761031",
                "snapshot": "https://trade.taobao.com/trade/detail/tradeSnap.htm?snapShot=true&tradeID=4244644335821941414"
            }
        }
    ],
    "actions": {
        "orderDetail": "https://trade.taobao.com/trade/detail/trade_order_detail.htm",
        "viewLogistics": True,
        "requestAfterSale": True,
        "initiateExchange": True,
        "invoice": True,
        "addRemark": True
    }
}


class SaiNiuAPI(object):
    def __init__(self, userNick='', buyerEid='', orderId='', AccessId='', AccessKey=''):
        self.userNick = userNick
        self.buyerEid = buyerEid
        self.orderId = orderId
        # self.base_url = config.QN_URL
        self.base_url = "http://192.168.1.162:3030"
        self.AccessType = 0
        self.AccessId = AccessId
        self.AccessKey = AccessKey
        self.ForceLogin = False

    # 获取买家订单列表
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_buyer_order(self):
        url = f"{self.base_url}/SaiNiuApi/Api"
        print('发送请求：', url)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {
            "userNick": self.userNick,
            "buyerEid": self.buyerEid,
            "orderId": self.orderId
        }
        postname = 'GetBuyerOrder'
        data = json.dumps(payload)
        # 构造完整的 URL，包含查询参数
        url = f"{url}?&post={postname}&data={data}"
        # 发送 POST 请求
        response = requests.post(url)
        print("订单信息:", response.json())

    # 返回用户订单信息
    @staticmethod
    def get_response(response):
        '''
            [订单号（orderid):1111
            时间（paytime):111
            购买商品（sku)：111]
        '''
        orderInfo = data_['orderInfo']
        orderid = orderInfo['orderId']
        paytime = orderInfo['payTime']
        sku = data_['items']['sku']
        return f'[订单号（orderid):{orderid},时间（paytime):{paytime},购买商品（sku)：{sku}]'

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_auth_login(self):
        url = f"{self.base_url}/SaiNiuApi/Access"
        print('发送请求：', url)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {
            "AccessType": self.AccessType,
            "AccessId": self.AccessId,
            "AccessKey": self.AccessKey,
            "ForceLogin": False,
            "EndCall": 0
        }
        postname = "Init"
        data = json.dumps(payload)
        # 构造完整的 URL，包含查询参数
        url = f"{url}?&post={postname}&data={data}"
        # 发送 POST 请求
        response = requests.post(url)
        print("授权信息:", response.json())

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_history_data(self):
        url = f"{self.base_url}/SaiNiuApi/Api"
        print('发送请求：', url)
        payload = {
            "userNick": self.userNick,
            "buyerUid": self.buyerEid,
            "pageSize": 20
        }
        postname = "GetRemoteMsgHistory"
        data = json.dumps(payload)
        # 构造完整的 URL，包含查询参数
        url = f"{url}?&post={postname}&data={data}"
        # 发送 POST 请求
        response = requests.post(url)
        print("授权信息:", response.json())

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_ship_info(self):
        url = f"{self.base_url}/SaiNiuApi/Api"
        print('发送请求：', url)
        payload = {
            "userNick": self.userNick,
            "orderId": self.orderId,
        }
        postname = "GetOrderLogistics"
        data = json.dumps(payload)
        # 构造完整的 URL，包含查询参数
        url = f"{url}?&post={postname}&data={data}"
        # 发送 POST 请求
        response = requests.post(url)
        print("发货信息:", response.json())


# 千牛账号，用户id
# sn_api = SaiNiuAPI('tb235688149:wsy', '2208461655683')
# sn_api.get_buyer_order()

sn_api = SaiNiuAPI(AccessId='max1015070108@gmail.com', AccessKey='MTAxNTA3MDEwOA')
sn_api.get_auth_login()

# sn_api = SaiNiuAPI('tb235688149:wsy', '2208461655683')
# sn_api.get_history_data()

#sn_api = SaiNiuAPI('tb235688149:wsy', '2208461655683')
#sn_api.get_ship_info(userNick="tb235688149:wsy", orderId="")
