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
import global_val

def write_error(content):
    with open("error.txt", encoding='utf-8', mode='a+') as fail_file:
        fail_file.write(content)
        fail_file.write('\n')

# error_file = []

class WordConvertToOther:
    def DocToDocx(docpath):
        '''将doc转存为docx'''
        logging.info("开始转换: {}".format(docpath))
        print("开始转换: {}".format(docpath))
        try:
            # CoInitialize初始化,为线程和word对象创建一个套间，令其可以正常关联和执行
            pythoncom.CoInitialize()
            # 用DispatchEx()的方式启动MS Word或与当前已执行的MS Word建立连结
            word = DispatchEx('Word.Application')
            # 打开指定目录下doc文档
            doc = word.Documents.Open(docpath)
            # 将打开的doc文档存储为docx
            doc.SaveAs(re.sub('.doc$', '.docx', docpath), FileFormat=12)
            # 关闭doc文档
            doc.Close()
        except Exception as e:
            # 报错则输出报错文件
            logging.error(docpath + '：无法打开')
            print(docpath + '：无法打开')
            global_val.error_file.append(f"{docpath} 无法打开: {str(e)}")
            write_error(f"{docpath} 无法打开: {str(e)}")
        else:
            # 无报错输出转换完成
            logging.info(os.path.basename(docpath) + " ： 转换完成")
            print(os.path.basename(docpath) + " ： 转换完成")
        finally:
            # 关闭office程序
            word.Quit()
            # 释放资源
            pythoncom.CoUninitialize()

    def DocToPdf(docpath):
        '''将doc、docx转存为pdf'''
        logging.info("开始转换: {}".format(docpath))
        print("开始转换: {}".format(docpath))
        try:
            pythoncom.CoInitialize()
            word = DispatchEx('Word.Application')
            doc = word.Documents.Open(docpath)
            doc.SaveAs(re.sub('\.doc.*', '.pdf', docpath), FileFormat=17)
            doc.Close()
        except Exception as e:
            logging.error(docpath + '：无法打开: {}'.format(e))
            print(docpath + '：无法打开: {}'.format(e))
            global_val.error_file.append(f"{docpath} 无法打开: {str(e)}")
            write_error(f"{docpath} 无法打开: {str(e)}")
        else:
            logging.info(os.path.basename(docpath) + " ： 转换完成")
            print(os.path.basename(docpath) + " ： 转换完成")
        finally:
            word.Quit()
            pythoncom.CoUninitialize()

    def PPTToPdf(docpath):
        """
        PPT文件导出为pdf格式
        :param filename: PPT文件的名称
        :param output_filename: 导出的pdf文件的名称
        :return:
        """
        # 2). 打开PPT程序
        # ppt_app = win32com.client.Dispatch('PowerPoint.Application')
        # # ppt_app.Visible = True  # 程序操作应用程序的过程是否可视化

        # # 3). 通过PPT的应用程序打开指定的PPT文件
        # # filename = "C:/Users/Administrator/Desktop/PPT办公自动化/ppt/PPT素材1.pptx"
        # # output_filename = "C:/Users/Administrator/Desktop/PPT办公自动化/ppt/PPT素材1.pdf"
        # ppt = ppt_app.Presentations.Open(path)

        # # 4). 打开的PPT另存为pdf文件。17数字是ppt转图片，32数字是ppt转pdf。
        # ppt.SaveAs(re.sub('\.ppt.*', '.pdf', path), 32)
        # logging.info(os.path.basename(path) + " ： 转换完成")
        # # 退出PPT程序
        # ppt_app.Quit()
        logging.info("开始转换: {}".format(docpath))
        print("开始转换: {}".format(docpath))
        dest_file = re.sub('.pptx?$', ".pdf", docpath)
        if os.path.exists(dest_file):
            logging.error(f"文件 {dest_file} 已存在")
            print(f"文件 {dest_file} 已存在")
            return
        try:
            # CoInitialize初始化,为线程和word对象创建一个套间，令其可以正常关联和执行
            pythoncom.CoInitialize()
            # 用DispatchEx()的方式启动MS Word或与当前已执行的MS Word建立连结
            word = DispatchEx('PowerPoint.Application')
            # 打开指定目录下doc文档
            doc = word.Presentations.Open(docpath)
            # 将打开的doc文档存储为docx
            doc.SaveAs(re.sub('.pptx?$', ".pdf", docpath), FileFormat=32)
            # 关闭doc文档
            doc.Close()
        except Exception as e:
            # 报错则输出报错文件
            logging.error(docpath + '：无法打开, {}'.format(e))
            print(docpath + '：无法打开, {}'.format(e))
            global_val.error_file.append(f"{docpath} 无法打开: {str(e)}")
            write_error(f"{docpath} 无法打开: {str(e)}")
        else:
            # 无报错输出转换完成
            logging.info(os.path.basename(docpath) + " ： 转换完成")
            print(os.path.basename(docpath) + " ： 转换完成")
        finally:
            # 关闭office程序
            word.Quit()
            # 释放资源
            pythoncom.CoUninitialize()
