# microsoft
#!/usr/bin/env python
# encoding: utf-8

"""
@author: sean10
@Date: 2021/4/23 18:26
@desc: 
======================

======================
"""
import os, re
import threading
import pythoncom
from win32com.client import DispatchEx
import multiprocessing
import time
import win32com.client
import glob
import yaml
import shutil
import logging
import pathlib
from lib import WordConvertToOther
import global_val
from multiprocessing import freeze_support
freeze_support()
log_file = open("microsoft2pdf.log", encoding="utf-8", mode="a")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    stream=log_file)

# error_file = []

# class WordConvertToOther:
#     def DocToDocx(docpath):
#         '''将doc转存为docx'''
#         logging.info("开始转换: {}".format(docpath))
#         print("开始转换: {}".format(docpath))
#         try:
#             # CoInitialize初始化,为线程和word对象创建一个套间，令其可以正常关联和执行
#             pythoncom.CoInitialize()
#             # 用DispatchEx()的方式启动MS Word或与当前已执行的MS Word建立连结
#             word = DispatchEx('Word.Application')
#             # 打开指定目录下doc文档
#             doc = word.Documents.Open(docpath)
#             # 将打开的doc文档存储为docx
#             doc.SaveAs(re.sub('.doc$', '.docx', docpath), FileFormat=12)
#             # 关闭doc文档
#             doc.Close()
#         except Exception as e:
#             # 报错则输出报错文件
#             logging.info(docpath + '：无法打开')
#             print(docpath + '：无法打开')
#             error_file.append(f"{docpath} 无法打开: {str(e)}")
#         else:
#             # 无报错输出转换完成
#             logging.info(os.path.basename(docpath) + " ： 转换完成")
#             print(os.path.basename(docpath) + " ： 转换完成")
#         finally:
#             # 关闭office程序
#             word.Quit()
#             # 释放资源
#             pythoncom.CoUninitialize()

#     def DocToPdf(docpath):
#         '''将doc、docx转存为pdf'''
#         logging.info("开始转换: {}".format(docpath))
#         print("开始转换: {}".format(docpath))
#         try:
#             pythoncom.CoInitialize()
#             word = DispatchEx('Word.Application')
#             doc = word.Documents.Open(docpath)
#             doc.SaveAs(re.sub('\.doc.*', '.pdf', docpath), FileFormat=17)
#             doc.Close()
#         except Exception as e:
#             logging.info(docpath + '：无法打开: {}'.format(e))
#             print(docpath + '：无法打开: {}'.format(e))
#             error_file.append(f"{docpath} 无法打开: {str(e)}")

#         else:
#             logging.info(os.path.basename(docpath) + " ： 转换完成")
#             print(os.path.basename(docpath) + " ： 转换完成")
#         finally:
#             word.Quit()
#             pythoncom.CoUninitialize()

#     def PPTToPdf(docpath):
#         """
#         PPT文件导出为pdf格式
#         :param filename: PPT文件的名称
#         :param output_filename: 导出的pdf文件的名称
#         :return:
#         """
#         # 2). 打开PPT程序
#         # ppt_app = win32com.client.Dispatch('PowerPoint.Application')
#         # # ppt_app.Visible = True  # 程序操作应用程序的过程是否可视化

#         # # 3). 通过PPT的应用程序打开指定的PPT文件
#         # # filename = "C:/Users/Administrator/Desktop/PPT办公自动化/ppt/PPT素材1.pptx"
#         # # output_filename = "C:/Users/Administrator/Desktop/PPT办公自动化/ppt/PPT素材1.pdf"
#         # ppt = ppt_app.Presentations.Open(path)

#         # # 4). 打开的PPT另存为pdf文件。17数字是ppt转图片，32数字是ppt转pdf。
#         # ppt.SaveAs(re.sub('\.ppt.*', '.pdf', path), 32)
#         # logging.info(os.path.basename(path) + " ： 转换完成")
#         # # 退出PPT程序
#         # ppt_app.Quit()
#         logging.info("开始转换: {}".format(docpath))
#         print("开始转换: {}".format(docpath))
#         dest_file = re.sub('.pptx?$', ".pdf", docpath)
#         if os.path.exists(dest_file):
#             logging.error(f"文件 {dest_file} 已存在")
#             print(f"文件 {dest_file} 已存在")
#             return
#         try:
#             # CoInitialize初始化,为线程和word对象创建一个套间，令其可以正常关联和执行
#             pythoncom.CoInitialize()
#             # 用DispatchEx()的方式启动MS Word或与当前已执行的MS Word建立连结
#             word = DispatchEx('PowerPoint.Application')
#             # 打开指定目录下doc文档
#             doc = word.Presentations.Open(docpath)
#             # 将打开的doc文档存储为docx
#             doc.SaveAs(re.sub('.pptx?$', ".pdf", docpath), FileFormat=32)
#             # 关闭doc文档
#             doc.Close()
#         except Exception as e:
#             # 报错则输出报错文件
#             logging.error(docpath + '：无法打开, {}'.format(e))
#             print(docpath + '：无法打开, {}'.format(e))
#             error_file.append(f"{docpath} 无法打开: {str(e)}")

#         else:
#             # 无报错输出转换完成
#             logging.info(os.path.basename(docpath) + " ： 转换完成")
#             print(os.path.basename(docpath) + " ： 转换完成")
#         finally:
#             # 关闭office程序
#             word.Quit()
#             # 释放资源
#             pythoncom.CoUninitialize()

# 使用os模块的walk函数，搜索出指定目录下的全部PDF文件
# 获取同一目录下的所有PDF文件的绝对路径
def getFileName(filedir):

    file_list = [os.path.join(root, filespath) \
                 for root, dirs, files in os.walk(filedir) \
                 for filespath in files \
                 if str(filespath).lower().endswith('pptx') or str(filespath).lower().endswith('ppt') or \
                     str(filespath).lower().endswith('docx') or str(filespath).lower().endswith('doc')
                 ]
    return file_list if file_list else []

def generate_backup(files, old_root_path, backup_path):
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    for file in files:
        file = pathlib.Path(file)
        logging.info(f"{file}, {old_root_path}")
        # temp_file = re.sub(old_root_path, "", file)
        temp_file = file.relative_to(old_root_path)
        new_path = os.path.join(backup_path, temp_file)
        new_file_parent = os.path.dirname(new_path)
        if not os.path.exists(new_file_parent):
            os.makedirs(new_file_parent)
        try:
            shutil.copy(file, new_path)
            logging.info(f"复制{file}到{new_path}")
            print(f"复制{file}到{new_path}")
        except Exception as e:
            logging.info("fail to copy {} {} for {}".formaSt(file, new_path, str(e)))
            print("fail to copy {} {} for {}".format(file, new_path, str(e)))
        
        

if __name__ == '__main__':
    # 控制线程最大并发数为12
    # 线程锁
    # 当前脚本目录绝对路径
    multiprocessing.freeze_support()

    time1 = time.time()
    with open("./conf.yaml", 'r', encoding='utf-8') as yml_f:
        data = yaml.load(yml_f, Loader=yaml.SafeLoader)

    path = data.get('path')
    backup_path = data.get("backup_path")
    path = os.path.realpath(path)
    
    files = getFileName(path)
    generate_backup(files, path, backup_path)

    p = multiprocessing.Pool(processes=10)
    # result = self.get_perf_counter_in_specified_ip(osd, ip)
    result = []
    logging.info(f"{files}")
    # for a, b, c in os.walk(pre):
    for file in files:
        if re.search('\.doc', file) != None:
            result.append(p.apply_async(WordConvertToOther.DocToPdf, args=(file, )))
        if re.search('\.pptx?$', file) != None:
            result.append(p.apply_async(WordConvertToOther.PPTToPdf, args=(file, )))
            # WordConvertToOther.PPTToPdf(pre + file)
    p.close()
    p.join()
    result_data = []
    cnt = 0
    for i in result:
        data = i.get()
        cnt += 1
        # logging.info(json.dumps(data, indent=4))
        result_data.append(data)
    time2 = time.time()
    logging.info('总共耗时：%s s. 处理 %d 个文件' %(time2 - time1, cnt))
    print('总共耗时：%s s. 处理 %d 个文件' %(time2 - time1, cnt))
    logging.info("失败文件: ")
    print("失败文件详见error.txt ")
    print(global_val.error_file)
    for file in global_val.error_file:
        logging.info(file)
        print(file)
    log_file.close()





