# AT_83TZKCOVuq7OJ2WSVCRZuFyZwuxnphYP APP_TOKEN
# 尊敬的用户，你的UID是：UID_uQwquKqBNPWTloEbEbPL6gq1wbRj
# https://wxpusher.zjiecode.com/wxuser/?type=1&id=80213#/follow
# {
#   "appToken":"AT_xxx",//必传
#   "content":"<h1>H1标题</h1><br/><p style=\"color:red;\">欢迎你使用WxPusher，推荐使用HTML发送</p>",//必传
#   //消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度20(微信只能显示20)，可以不传，不传默认截取content前面的内容。
#   "summary":"消息摘要",
#   //内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签，推荐使用这种) 3表示markdown
#   "contentType":2,
#   //发送目标的topicId，是一个数组！！！，也就是群发，使用uids单发的时候， 可以不传。
#   "topicIds":[
#       123
#   ],
#   //发送目标的UID，是一个数组。注意uids和topicIds可以同时填写，也可以只填写一个。
#   "uids":[
#       "UID_xxxx"
#   ],
#   //原文链接，可选参数
#   "url":"https://wxpusher.zjiecode.com",
#   //是否验证订阅时间，true表示只推送给付费订阅用户，false表示推送的时候，不验证付费，不验证用户订阅到期时间，用户订阅过期了，也能收到。
#   //verifyPay字段即将被废弃，请使用verifyPayType字段，传verifyPayType会忽略verifyPay
#   "verifyPay":false,
#   //是否验证订阅时间，0：不验证，1:只发送给付费的用户，2:只发送给未订阅或者订阅过期的用户
#   "verifyPayType":0
# }

# {
#     "code": 1000, //状态码，非1000表示有异常
#     "msg": "处理成功",//提示消息
#     "data": [ //每个uid/topicid的发送状态，和发送的时候，一一对应，是一个数组，可能有多个
#         {
#             "uid": "UID_xxx",//用户uid
#             "topicId": null, //主题ID
#             "messageId": 121,//废弃⚠️，请不要再使用，后续会删除这个字段
#             "messageContentId": 2123,//消息内容id，调用一次接口，生成一个，你可以通过此id调用删除消息接口，删除消息。本次发送的所有用户共享此消息内容。
#             "sendRecordId": 12313,//消息发送id，每个uid用户或者topicId生成一个，可以通过这个id查询对某个用户的发送状态
#             "code": 1000, //1000表示发送成功
#             "status": "创建发送任务成功"
#         }
#     ],
#     "success": true
# }
# ret['code'] == 1000 success
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from loguru import logger
import requests
from run import constants


@logger.catch
def wx_push_content(content):
    """
    :param content msg content
    :return ret
    """
    if not constants.WeChat_push_flag:
        logger.warning(f"Not open WeChat msg push flag: {constants.WeChat_push_flag}, will skip push.")
        return False
    try:
        logger.debug(f"Will push wechat msg content: {content}")

        header = {
            "Content-Type": "application/json"
        }
        body = {
            "appToken": "AT_83TZKCOVuq7OJ2WSVCRZuFyZwuxnphYP",
            "content": content,
            "summary": "消息摘要",
            "contentType": 1,
            "uids": [
                "UID_uQwquKqBNPWTloEbEbPL6gq1wbRj"
            ],
            "url": "https://caozhaoqi.github.io",
            "verifyPay": False,
            "verifyPayType": 0
        }
        request_url = "https://wxpusher.zjiecode.com/api/send/message"

        ret = requests.post(request_url, data=json.dumps(body), headers=header)
        logger.debug(f"Push wechat msg response: {ret.content}")
    except Exception as e:
        ret = e
        logger.error(f"Error, push msg to wechat error, detail: {e}")
    return ret
