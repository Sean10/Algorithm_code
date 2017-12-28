#coding:utf-8
#
#
#
# 参考git@github.com:taba256/nicoseiga-download.git
# 不过没能理解那个转码解密的过程，暂时放下了
#
#
#
from bs4 import BeautifulSoup
from PIL import Image
import requests
import base64
import threading
import re
import json

cookies = {'area':"TW",
            'lang':"en-us",
            'nicoid':"1514362455.711754430",
            'user_session':"user_session_54549882_9234fe69cf1b92567badaf4e4323ea574c3f76a4dae3f385b842a9692b8785a5"
             }


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def data_out(data):
    fo = open("./data.jpg", "w")

    fo.write(data)

    fo.close()

def is_img(tag):
    return tag.name=='img' and tag.has_attr('data-original')

def spider_home_page():


    url = "http://seiga.nicovideo.jp/watch/mg147902?track=ct_episode"
    req = requests.get(url, cookies=cookies)

    url_list = []
    html = BeautifulSoup(req.content,"lxml")
    element = html.find_all(is_img)
    #print(element)
    for i in element:
        #print(i.attrs)
        #if i.has_attr('data-original'):
        print(i['data-original'])
        url_list.append(i['data-original'])
    #data_out(element.prettify())
    for i, j in enumerate(url_list):
        thread = threading.Thread(target=save_file,args=(i,j))
        thread.start()
    #driver.close()

def save_file(i,j):
    with open('28/{0}.jpg'.format(i), 'wb') as file:
        file.write(requests.get(j).content)

def spider_newest():
    url = "https://drm.nicoseiga.jp/image/d48eb251b7b9d5275ece2ee0347df9d101b9364a_17528/7733596p"
    #'x-requested-with': 'XMLHttpRequest',
    keystring = re.findall(r"[0-9a-fA-F]{40}",url)[0]
    key = [0 for i in range(8)]
    for i in range(8):
        key[i] = int(keystring[2*i:(2*i+2)],16)
    print(key)
    #print(key)
    header = {'Referer': 'http://seiga.nicovideo.jp/watch/mg291445'}
    req = requests.get(url, cookies=cookies,headers=header)



    #jsen = req.content.decode()
    #print(req.content)




    #f = open("xxx","rb")
    f = req.content
    temp_list = []
    for i,x in enumerate(f):
        #temp_list.append(int.from_bytes(x,byteorder='big'))
        #print(x)
        temp_list.append(x^key[i&7])
        #temp_list()
    #print(temp_list)
    with open("i.jpg","wb") as of:
        for i in temp_list:
            #print(i)
            #print(i.to_bytes(1,byteorder='big'))
            of.write(i.to_bytes(2,byteorder='big'))

    #print(f.readline().decode())



    # try:
    #     strj = json.loads(jsonen)
    # except Exception as err:
    #     # 返回值不是json类型
    #     print(err)
    #     print(req.content)
    #     print('程序出现错误，停止运行')
    #
    # print(json.dumps(strj, ensure_ascii=False, sort_keys=False, indent=4))

if __name__ == "__main__":
    #spider_home_page()
    spider_newest()
    #print(data)
    # d = requests.get("https://drm.nicoseiga.jp/image/35bf34ccf294989548cdc0e546c43d0e31f01131_17527/7713840p")
    # data_out(d.content)
    #img = Image.open("data.png")
    #img.show()
    pass;
    #f = open("7713885p","rb")
    #img = io.BytesIO(f.read())

    #x = f.read().decode()
    #x = "data:image/jpg;"+x
    # img = Image.open("7713885p")
    # img.show()
    #print(x.decode())
    #img = f.read().decode("utf-8")
    #fp = open("77p_new","w")
    #fp.write(f.read)
    #fp.close()
    #f.close()
    #print(imghdr.what("77p_new"))
