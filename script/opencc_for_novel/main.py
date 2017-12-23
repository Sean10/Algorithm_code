import opencc
import os
import sys
import chardet


class novel_trans:
    openCC = opencc.OpenCC('t2s')

    def __init__(self):
        self.f_list = os.listdir(os.getcwd())

    def open_file(self):
        for i in self.f_list:
            novel_trans.f_convert(self,i)

    def f_convert(self,i):
        if os.path.splitext(i)[1] == '.txt':
            i2s = novel_trans.openCC.convert(os.path.splitext(i)[0])
            print(i2s)
            fp_in = open(i, "rb")
            code = chardet.detect(fp_in.read())
            fp_in.close()

            fp_in = open(i, "r", encoding=code['encoding'])

            ##print(code)
            fp_out = open(i2s+"trans.txt","w")
            fp2s = novel_trans.openCC.convert(fp_in.read())
            fp_out.write(fp2s)
            fp_in.close()
            fp_out.close()



if __name__ == '__main__':
    test = novel_trans()
    test.open_file()
