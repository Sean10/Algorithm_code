import json
import urllib.request
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import sys
import signal
import yaml
import requests


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


def main():
    # print("Get Work!")
    localtime = time.asctime(time.localtime(time.time()))  # 报时，免得程序卡住不知道～
    # url = 'https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},{"tsMemorySize":"32gb"},{"dimensionScreensize":"13inch"},{"dimensionRelYear":"2020"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}'
    # url = 'https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},{"tsMemorySize":"32gb"},{"dimensionScreensize":"16inch"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}'
    # url = 'https://www.apple.com.cn/shop/refurbished/mac/13-%E8%8B%B1%E5%AF%B8-macbook-pro-16gb'
    url = 'http://www.ccgp.gov.cn/cggg/zygg/index_{}.htm'
    headers = {'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}  # 添加headers防止官网认为是爬虫而屏蔽访问
    result = []
    filtered = []
    for i in range(1,100):
        req = requests.get(url.format(str(i)), headers=headers)
        res = req.status_code
            # print("something error {}".format(str(e)))
            # if 301 == e.status:
        if res != 200:
            print("{} something error".format(localtime))
            break
        else:
            print("fetch {} success".format(url.format(str(i))))
    # except Exception as e:
    #     print("pause after sleep.")
    # print(body)
        req.encoding = req.apparent_encoding
        content = BeautifulSoup(req.text, 'html.parser')
        # with open("output.html", "w", encoding='utf-8') as f:
        #     f.write(content.prettify())
        ans = content.select('div.vF_detail_relcontent_lst  li')
        for item in ans:
            title = item.a.attrs['title']
            href = "http://www.ccgp.gov.cn/cggg/zygg/{}".format(item.a.attrs['href'])
            temp = {"title": title,"href": href}
            result.append(temp)
            if "宣传" not in title:
                continue
            print(temp)
            filtered.append(temp)
            
    # time.sleep(10)
    with open("result.yaml", "w", encoding='utf-8') as f: 
        yaml.dump(result, f, allow_unicode=True)
    with open('filter.yaml', "w") as f:
        yaml.dump(filtered, f, allow_unicode=True)

if __name__ == "__main__":
    init_signal()
    # send_mail("macbook有货了", 'hello world', "644540267@qq.com")
    main()
