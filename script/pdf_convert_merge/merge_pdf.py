# merge
#!/usr/bin/env python
# encoding: utf-8

"""
@author: sean10
@Date: 2019/12/5 18:52
@desc: 
======================

======================
"""

# -*- coding:utf-8*-
# 利用PyPDF2模块合并同一文件夹下的所有PDF文件
# 只需修改存放PDF文件的文件夹变量：file_dir 和 输出文件名变量: outfile

import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,SimpleDocTemplate
import fitz
import time
import io
import glob

rm_targets = []

# 使用os模块的walk函数，搜索出指定目录下的全部PDF文件
# 获取同一目录下的所有PDF文件的绝对路径
def getFileName(filedir):

    file_list = [os.path.join(root, filespath) \
                 for root, dirs, files in os.walk(filedir) \
                 for filespath in files \
                 if str(filespath).lower().endswith('pdf')
                 ]
    return file_list if file_list else []

def pic2pdf_1(image_path):
    for img in sorted(glob.glob(image_path + "\*.jpg")):
        imgdoc = fitz.open(img)
        doc = fitz.open()
        pdfbytes = imgdoc.convertToPDF()
        imgpdf = fitz.open("pdf", pdfbytes)
        doc.insertPDF(imgpdf)
        doc.save(os.path.join(image_path, "{}.pdf".format(img)))
    

# 合并同一目录下的所有PDF文件
def MergePDF(filepath, outfile):

    output = PdfFileWriter()
    outputPages = 0
    

    if os.path.exists(os.path.join(filepath, outfile)):
        os.remove(os.path.join(filepath, outfile))

    pdf_fileName = getFileName(filepath)
    if pdf_fileName:
        temp_file = "{}_name".format(pdf_fileName[0])
        for pdf_file in pdf_fileName:
            temp_file = "{}_name".format(pdf_file)
            
            print("路径：%s"%pdf_file)

            # 读取源PDF文件
            input = PdfFileReader(open(pdf_file, "rb"), strict=False)

            # 获得源PDF文件中页面总数
            pageCount = input.getNumPages()
            outputPages += pageCount
            print("页数：%d"%pageCount)

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            pdfmetrics.registerFont(TTFont('Song', "C://Windows//Fonts//simsun.ttc"))
            pdfmetrics.registerFontFamily("Song", normal="Song", bold="Song", italic="Song", boldItalic="Song")
            # can.setFont("HeiTi", 14)
            # can.drawString(10, 100, "{}".format(pdf_file))
            # can.save()

            Style=getSampleStyleSheet()

            bt = Style['Normal']     #字体的样式
            bt.fontName='Song'    #使用的字体
            bt.fontSize=14            #字号
            bt.wordWrap = 'CJK'    #该属性支持自动换行，'CJK'是中文模式换行，用于英文中会截断单词造成阅读困难，可改为'Normal'
            bt.firstLineIndent = 0  #该属性支持第一行开头空格
            bt.leading = 20             #该属性是设置行距

            # ct=Style['Normal']
            # ct.fontName=''
            # ct.fontSize=24
            # ct.alignment=0           #居中

            # ct.textColor = colors.red
            name = pdf_file
            if pdf_file.endswith('.jpg.pdf'):
                name = name[:-8]
            elif pdf_file.endswith('.pdf'):
                name = name[:-4]
            elif pdf_file.endswith('.PDF'):
                name = name[:-4]
            #if ".jpg" in pdf_file:
                #name = pdf_file[:-4]
            name = name.split('\\')[-1]
            print(name)

            t = Paragraph(name,bt)
            
            pdf=SimpleDocTemplate(temp_file)
            pdf.multiBuild([t])
            # pdf.close()
            

            name_pdf = PdfFileReader(open(temp_file, "rb"), strict=False)
            output.addPage(name_pdf.getPage(0))
            output.addBlankPage()
            # 分别将page添加到输出output中
            for iPage in range(pageCount):
                output.addPage(input.getPage(iPage))
            if pageCount % 2:
                output.addBlankPage()
            rm_targets.append(temp_file)

        print("合并后的总页数:%d."%outputPages)
        # 写入到目标PDF文件
        outputStream = open(os.path.join(filepath, outfile), "wb")
        print(output)
        output.write(outputStream)
        outputStream.close()
        print("PDF文件合并完成！")

    else:
        print("没有可以合并的PDF文件！")

# 主函数
def main():
    time1 = time.time()
    # file_dir = r'E:\Cheats' # 存放PDF的原文件夹
    # file_dir = os.getcwd()
    file_dir = 'D:\\新建文件夹\\'
    pic2pdf_1(file_dir)
    outfile = "Cheat_Sheets.pdf" # 输出的PDF文件的名称
    MergePDF(file_dir, outfile)
    time2 = time.time()
    print('总共耗时：%s s.' %(time2 - time1))

main()

