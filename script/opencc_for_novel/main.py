# _*_ coding: utf-8 _*_

import opencc
import os
import sys
import chardet
import argparse
from tqdm import tqdm

def get_filelist():
    temp_list = os.listdir(os.getcwd())
    f_list = []
    print(args.recursive)
    if args.recursive:
        for i in temp_list:
            # print(os.getcwd())
            # print(i)
            path = os.path.join(os.getcwd(),i)
            if os.path.isdir(path):
                temp_file = os.listdir(i)
                for x in temp_file:
                    temp_list.append(os.path.join(path,x))
            else:
                f_list.append(i)
    else:
        for i in temp_list:
            if os.path.isdir(i):
                continue;
            f_list.append(i)
    return f_list

def open_file():
    for i in tqdm(f_list):
        f_convert(i)

def f_convert(i):
    if os.path.splitext(i)[1] == '.txt':
        if "trans" in i:
            return ;

        i2s = openCC.convert(os.path.splitext(i)[0])
        print(i2s)
        fp_in = open(i, "rb")
        code = chardet.detect(fp_in.read())
        fp_in.close()

        fp_in = open(i, "r", encoding=code['encoding'])

            ##print(code)
        fp_out = open(i2s+"_trans.txt","w")
        fp2s = openCC.convert(fp_in.read())
        fp_out.write(fp2s)
        fp_in.close()
        fp_out.close()


if __name__ == '__main__':
    openCC = opencc.OpenCC('t2s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-r',"--recursive",action="store_true",help="trans the text recursively")
    args = parser.parse_args()

    f_list = get_filelist()
    open_file()
