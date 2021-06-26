import json
from typing import Dict
import urllib.request
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import sys
import signal
import yaml
import aiohttp
import chardet
import asyncio

result = []
filtered = []

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

def shutdownFunction(signalnum, frame):
    print("receive exit signal, exit normally.")
    sys.exit(0)

def init_signal():
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(sig, shutdownFunction)

# while True:
async def html(url: str, params: Dict) ->str:
    code = 'utf-8'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    async with aiohttp.ClientSession() as session:
        # 老版本aiohttp没有verify参数，如果报错卸载重装最新版本
        async with session.get(url, headers=headers, timeout=10, verify_ssl=False, params=params) as r:
            content = await r.read()
            code = chardet.detect(content)['encoding']
            # text()函数相当于requests中的r.text，不带参数则自动识别网页编码，同样会拖慢程序。r.read()相当于requests中的r.content
            return await r.text(encoding=code, errors='ignore')

async def read_one(url, params):
    req = await html(url, params)
    # print(req)
    content = BeautifulSoup(req, 'html.parser')
        # with open("output.html", "w", encoding='utf-8') as f:
        #     f.write(content.prettify())
    ans = content.select('div.vT-srch-result-list  li')
    print(len(ans))
    for item in ans:
        # print(item)
        title = item.a.text.strip()
        href = item.a.attrs['href']
        temp = {"title": title,"href": href}
        print(temp)
        result.append(temp)
        if "宣传" not in title:
            continue
        print(temp)
        filtered.append(temp)
            
    # time.sleep(10)
 

def read_many(links: list):
    loop = asyncio.get_event_loop()
    to_do = [read_one(item["url"], item["params"]) for item in links]
    loop.run_until_complete(asyncio.wait(to_do))
    # 或loop.run_until_complete(asyncio.gather(*to_do))这两行代码作用似乎没啥区别
    loop.close()


def main2():
    total = 20
    # url = 'http://www.ccgp.gov.cn/cggg/zygg/index_{}.htm'
    url = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1'
    keyword = '宣传片'
    start_time = '2020:01:01'
    end_time = '2020:10:09'
    page_num = 1
    Tag =2

    params = {
        'searchtype': '1',
        'page_index': page_num,
        'bidSort': '0',
        'pinMu': '0',
        'bidType': '1',
        'kw': keyword,
        'start_time': start_time,
        'end_time': end_time,
        'timeType': '6'
    }
    
    params_list = [params for i in range(total)]
    for i in range(total):
        params_list[i]['page_index'] = i
    links = [{"url":url, "params": params} for i in range(total)]
    
#     links = [...]  # 要跑的所有链接列表
    read_many(links)
    with open("result.yaml", "w", encoding='utf-8') as f: 
        yaml.dump(result, f, allow_unicode=True)
    with open('filter.yaml', "w") as f:
        yaml.dump(filtered, f, allow_unicode=True)
        

if __name__ == "__main__":
    init_signal()
    main2()
