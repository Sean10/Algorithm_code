#!/usr/bin/env python
# encoding: utf-8

"""
@author: sean10
@Date: 2020/8/12 16:15
@desc: 
======================

TODO:next_siblings必须是相同的标签吗？如果我当前是div， 我想删掉剩下的同级<p>呢
======================
"""
import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk')
import win32com.client
from dateutil import parser
from datetime import datetime, timezone
import pytz
import re
from collections import OrderedDict
import time

from bs4 import BeautifulSoup
global_stack = OrderedDict()


def get_last_total_record(folder):
    messages = folder.Items
    if len(messages) <= 0:
        return None
    for message2 in reversed(messages):
        subject = message2.Subject
        if "晨会记录" in subject and re.findall(r"\d+月\d+日", subject):
            print(subject)
            receive_time = parser.parse(str(message2.ReceivedTime)).replace(tzinfo=None)
            curr_date = datetime.strptime(receive_time.strftime("%Y-%m-%d"), "%Y-%m-%d")
            print(receive_time)
            print(curr_date)
            # print(type(parser.parse(str(message2.ReceivedTime))))
            # print("curr", curr_date)
            # print(subject)
            sender = message2.SenderEmailAddress
            if sender != "":
                print("my sender:{}".format(sender))
            # 暂时放弃解析，尝试直接拼接看看


            return message2


def reply_message(message_temp, date_key, stack):
    item = message_temp.Reply()
    # 测试用，只发给自己
    # item = message_temp.Reply()
    item.Recipients.Add("1@example.com.cn")
    item.Recipients.Add("2@example.com.cn")
    item.Recipients.Add("3@example.com.cn")
    item.Recipients.Add("4@example.com.cn")
    item.Recipients.Add("5@example.com.cn")
    item.Recipients.Add("6@example.com.cn")
    # receive_time = parser.parse(str(message.ReceivedTime)).replace(tzinfo=None)
    # month = str(int(receive_time.strftime("%m")))
    # day = str(int(receive_time.strftime("%d")))
    item.Subject = "{}月{}日 {}".format(date_key[1], date_key[2], "晨会记录")
    subject = item.Subject
    bs = BeautifulSoup(item.HTMLBody, "lxml")
    with open("temp.html", "w", encoding='utf-8') as f:
        f.write(bs.prettify())
    bs = BeautifulSoup(open("temp.html", encoding='utf-8'), "lxml")
    for content in stack:
        new_soup = BeautifulSoup(content, "lxml")
        for p in reversed(new_soup.select("p")):
            bs.select("div.WordSection1")[0].insert(0, p)
    with open("new2.html", "w", encoding='utf-8') as f:
        f.write(bs.prettify())
    item.HTMLBody = bs.prettify()
    item.Save()
    item.Send()
    return subject

def main():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    print(outlook)
    accounts = win32com.client.Dispatch("Outlook.Application").Session.Accounts
    for account in accounts:
        print(account.DeliveryStore.DisplayName)

    def emailleri_al(folder, last_send_time):
        messages = folder.Items
        a = len(messages)
        print(a)
        # print(messages)
        if a > 0:
            for message2 in reversed(messages):
                subject = message2.Subject.encode("utf-8").decode('utf-8')
                if "晨会记录" in subject:
                    re_result = re.findall(r"(\d{4})[.-](\d+)[.-](\d+)", subject)
                    if not re_result:
                        continue
                    curr_day_key = re_result[0]

                    receive_time = parser.parse(str(message2.ReceivedTime)).replace(tzinfo=None)

                    if last_send_time > receive_time:
                        break
                    print(subject)
                    # print(type(parser.parse(str(message2.ReceivedTime))))
                    # print("curr", curr_date)
                    # print(subject)
                    sender = message2.SenderEmailAddress
                    if sender != "":
                        print("my sender:{}".format(sender))

                    bs = BeautifulSoup(message2.HTMLBody, "lxml")
                    tags = bs.select("div.WordSection1 > div")
                    content = message2.HTMLBody
                    content = re.sub(r"(<div(?! class=\"?Word)[\s\S]+?</div>)[\S\s]+(?=</div>)", "", content)
                    content = content.replace("""<p class=MsoNormal style='background:#C7EDCC'><b><span lang=EN-US style='font-size:12.0pt;font-family:"微软雅黑",sans-serif;color:black'>-----------------------------------------------------------------------------------------</span></p>""", "")
                    if tags:
                        with open("temp_new_{}.html".format(sender), "w", encoding='utf-8') as f:
                            f.write( message2.HTMLBody)

                    with open("new_{}.html".format(sender), "w", encoding='utf-8') as f:
                        f.write(content)

                    if curr_day_key not in global_stack:
                        global_stack[curr_day_key] = [content]
                    else:
                        global_stack[curr_day_key].append(content)
                    if last_send_time > receive_time:
                        break
                    # for line in content.split('\n'):
                    #     if "发件人" in line or "Hikvision" in line:
                    #         continue
                    #     print(line)
                continue


                print(account.DeliveryStore.DisplayName)
                pass

                try:
                    message2.Save()
                    message2.Close(0)
                except:
                    pass

    for account in accounts:
        if not "a@example.com.cn" == account.DisplayName:
            continue
        global inbox
        inbox = outlook.Folders(account.DeliveryStore.DisplayName)
        print("****Account Name**********************************")
        print("***************************************************")
        folders = inbox.Folders

        def test_replyall(folder):
            messages = folder.Items
            a = len(messages)
            print(a)
            # print(messages)
            if a > 0:

                for message2 in reversed(messages):
                    subject = message2.Subject
                    if "test" in subject:
                        print(subject)
                        receive_time = parser.parse(str(message2.ReceivedTime)).replace(tzinfo=None)
                        curr_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
                        # if curr_date > receive_time:
                        #     break
                        print(receive_time)
                        # print(type(parser.parse(str(message2.ReceivedTime))))
                        # print("curr", curr_date)
                        # print(subject)
                        sender = message2.SenderEmailAddress
                        if sender != "":
                            print("my sender:{}".format(sender))
                        content = message2.body
                        # print(content)
                        # 暂时先不折腾这个编码问题了。
                        # print("珅".encode('utf-8'))
                        # print(content.encode('utf-8'))
                        # print(content.encode('utf-8')[3:6])
                        # print(content.encode('utf-8')[3:6].decode('utf-8'))
                        # print(content.encode('utf-8').decode('utf-8'))
                        for line in content.split('\n'):
                            if "发件人" in line or "Hikvision" in line:
                                break
                            # print(line)
                        item = message2.ReplyAll()
                        item.CC += "a@example.com.cn"
                        item.Body = "hello world"
                        item.Save()
                        item.Send()
                        break

        message = None

        outbox_folder = None
        inbox_folder = None
        for folder in folders:
            if "已发送邮件" == str(folder):
                outbox_folder = folder
            elif "收件箱" == str(folder):
                inbox_folder = folder
                # test_replyall(outbox_folder)
        message = get_last_total_record(outbox_folder)
        last_send_time = re.findall(r'(\d+)月(\d+)日', message.Subject)[0]
        curr_year = datetime.now().strftime("%Y")
        print(last_send_time)
        last_send_time = datetime.strptime("{}-{}-{}".format(curr_year, last_send_time[0], str(int(last_send_time[1])+1)), "%Y-%m-%d")
        print(last_send_time)
                # reply_message(message)
        emailleri_al(inbox_folder, last_send_time)
        print(global_stack)
        print(message)
        while global_stack:
            temp = global_stack.popitem()
            key = temp[0]
            value = temp[1]
            print(key)
            if "8" in key and "18" in key:
                break

            temp_str = str(value)
            temp_list = ["b", "c", "d", "e"]
            for hello in temp_list:
                if hello in temp_str:
                    print(hello)
            subject = reply_message(message, key, value)
            time.sleep(20)
            message = get_last_total_record(outbox_folder)
            if subject == message.Subject:
                print(subject)
            print(message)


    print("Finished Succesfully")


if __name__ == "__main__":
    main()