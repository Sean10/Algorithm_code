#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-10-20 13:10
# @Author  : sean10
# @Site    : 
# @File    : test_tl.py
# @Software: PyCharm

"""
test tui li sudoku from sudokufans.org

"""

import requests
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
import re

threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

cookies = "__cfduid=df2b6bdb5b18f04b6b441b9c07832ac8b1570632906; PHPSESSID=37pga7s1fctjb3t77cg0ehreh3; c_userid=29143; c_username=sean10; ips4_IPSSessionFront=9mh6mnbs14vpah5jgc536egum0; light=1; yjs_id=fDE1NzE0NzMwNTU3NjU; ctrl_time=1"
headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,zh-TW;q=0.6,ja;q=0.5,zu;q=0.4",
        "cache-control": "no-cache", "pragma": "no-cache", "upgrade-insecure-requests": "1",
        "cookie": cookies}

def main():
    src_img = Image.open("tl.img.png")

    img_1 = src_img.crop((310, 0, 360, 40)).convert('L').point(table, '1')
    # img_1.save("temp.png")

    print(pytesseract.image_to_string(img_1,
                                      config='--psm 7 sudoku'))


def parse_img_src(src:str)->int:
    model = re.compile(r'(?<=tl.img.php\?t=)\d+')
    m = re.search(model, src).group(0)
    return int(m)


def spider(params=None):
    if not params:
        url = "http://www.sudokufans.org.cn/lx/tl.index.php"
    else:
        url = "http://www.sudokufans.org.cn/lx/tl.img.php"
    # cookies = {"__cfduid": "df2b6bdb5b18f04b6b441b9c07832ac8b1570632906", "PHPSESSID": "37pga7s1fctjb3t77cg0ehreh3",
    #            "c_userid": "29143", "c_username": "sean10", "ips4_IPSSessionFront": "9mh6mnbs14vpah5jgc536egum0",
    #            "light": "1", "yjs_id": "fDE1NzE0NzMwNTU3NjU", "ctrl_time": "1"}

    html = requests.get(url, params=params, headers=headers)
    if not params:
        return parse_img_src(html.text)
    print(html.url)
    print(html.headers)
    with open("temp.png", "wb") as f:
        f.write(html.content)
    content = BeautifulSoup(html.text, 'html.parser')
    with open("output.html", "w") as f:
        f.write(content.prettify())

def submit(ans):
    data = {f"find[{i}]": ans[i] for i in range(len(ans))}
    url = "http://www.sudokufans.org.cn/lx/fine2.php"
    html = requests.post(url, data=data, headers=headers)
    content = BeautifulSoup(html.text, 'html.parser')
    with open("temp.html", "w") as f:
        f.write(content.prettify())

if __name__ == "__main__":
    main()
    # submit(ans)
    # num = spider()
    # spider({"t": num})
