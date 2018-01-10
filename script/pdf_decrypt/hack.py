'''
虽然使用了多进程，但是因为依旧是通过python执行的，导致依旧只有1、2个进程使用到了CPU资源。
需要找一个方法能够让直接启动shell进行多进程操作，可能不行，还是需要shell直接进行
'''

import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

def decrypt(file):
    name = os.path.splitext(file)[0]
    p1 = subprocess.Popen(["pdf2ps",file])
    p1.wait()
    print("pdf2ps "+file)
    p2 = subprocess.Popen(["ps2pdf",name+".ps","hack_"+name+".pdf"])
    p2.wait()
    print("ps2pdf "+name+".ps "+"hack_"+name+".pdf")
    print("succeed to trans "+file)

if __name__ == '__main__':
    pool = ProcessPoolExecutor(max_workers=20)
    filelist = os.listdir(os.getcwd())
    for file in filelist:
        if os.path.splitext(file)[1] == '.pdf':
            if "hack_" in file:
                continue;
            future1 = pool.submit(decrypt,file)
            print(future1.result())
