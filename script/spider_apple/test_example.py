import json
import urllib.request
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import sys
import signal




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

def send_mail(title, article, receiver):
    host = 'smtp.qq.com'  # 这是QQ邮箱SMTP服务器的host，其他邮箱有不同可具体查询
    user = 'sean10@qq.com'#这是邮箱号
    password = 'irppsqhppevvbdec'#这是授权码，注意不是邮箱的密码或者QQ的密码！
    sender = user
    coding = 'utf8'
    message = MIMEText(article, 'plain', coding)
    message['From'] = Header(sender, coding)
    message['To'] = Header(receiver, coding)
    message['subject'] = Header(title, coding)

    try:
        mail_client = smtplib.SMTP_SSL(host, 465)#部分邮箱信道不同，又有可能没有开启SSL服务，具体查询
        mail_client.connect(host)
        mail_client.login(user, password)
        mail_client.sendmail(sender, receiver, message.as_string())
        mail_client.close()
        print('邮件已成功发送给:' + receiver)
    except Exception as e:
        print('发送失败! {}'.format(str(e)))
# while True:
def main():
    while True:
        # print("Get Work!")
        localtime = time.asctime(time.localtime(time.time()))  # 报时，免得程序卡住不知道～
        # url = 'https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},{"tsMemorySize":"32gb"},{"dimensionScreensize":"13inch"},{"dimensionRelYear":"2020"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}'
        # url = 'https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},{"tsMemorySize":"32gb"},{"dimensionScreensize":"16inch"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}'
        # url = 'https://www.apple.com.cn/shop/refurbished/mac/13-%E8%8B%B1%E5%AF%B8-macbook-pro-16gb'
        url = 'https://www.apple.com.cn/shop/refurbished/mac/13-%E8%8B%B1%E5%AF%B8-macbook-pro-32gb'
        headers = {'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}  # 添加headers防止官网认为是爬虫而屏蔽访问
        req = urllib.request.Request(url, headers=headers)
        res = 0
        try:
            rsp = urllib.request.urlopen(req)
            res = rsp.status
        except urllib.error.HTTPError  as e:
            # print("something error {}".format(str(e)))
            if 301 == e.status:
                print("{} 无货".format(localtime))
        except Exception as e:
            print("pause after sleep.")
        # print(body)
        if 200 == res:
            send_mail("macbook有货了", 'hello world', "644540267@qq.com")
            print("{} now 有货了".format(localtime))
        time.sleep(10)

if __name__ == "__main__":
    init_signal()
    # send_mail("macbook有货了", 'hello world', "644540267@qq.com")
    main()
