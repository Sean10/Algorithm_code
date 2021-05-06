# !/user/bin/env python
# -*- coding:utf-8 -*- 
# time: 2018/2/2--21:19
__author__ = 'Henry'

'''
爬取B站直播弹幕并发送跟随弹幕
'''

import requests, re
import time
import random
from Spiders.permutation import calc


def main():
    print('*' * 30 + '欢迎来到B站直播弹幕小助手' + '*' * 30)
    cookie = "SESSDATA=xx; DedeUserID=xxx; DedeUserID__ckMd5=xx; "
    # token = re.search(r'bili_jct=(.*?);', cookie).group(1)
    # csrf_token就是cookie中的bili_jct字段;且有效期是7天!!!
    token = "xx"
    print(token)

    # roomid = "23058701"
    while True:

        list1 = [int(i) for i in input("Enter some numbers:").strip().split(" ")]

        result = calc(list1)
        # 爬取:
        url = 'https://api.live.bilibili.com/ajax/msg'
        form = {
            'roomid': roomid,
            'visit_id': '',
            'csrf_token': token  
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Cookie': cookie
        }

        for barrage in result:
        
            # 跟随发送:
            url_send = 'https://api.live.bilibili.com/msg/send'
            data = {
                'color': '16777215',
                'fontsize': '25',
                'mode': '1',
                'msg': barrage,
                'rnd': int(time.time()),
                'roomid': roomid,
                'csrf_token': token,
                'csrf': token
            }



            try:


                html_send = requests.post(url_send, data=data, headers=headers)
                result = html_send.json()
                print(result)
                if result['msg'] == '你被禁言啦':
                    print('*' * 30 + '您被禁言啦!!! 跟随弹幕发送失败~' + '*' * 30)
                    exit()
                if result['code'] == 0 and result['msg'] == '':
                    print('*' * 30 + '[' + barrage + ']' + ' 跟随弹幕发送成功~' + '*' * 30)
                else:
                    print('*' * 30 + '[' + barrage + ']' + ' 跟随弹幕发送失败' + '*' * 30)
            except:
                print('*' * 30 + '[' + barrage + ']' + ' 跟随弹幕发送失败' + '*' * 30)
            time.sleep(1)

