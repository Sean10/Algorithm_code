
import os
import subprocess
from concurrent.futures import thread

filelist = os.listdir(os.getcwd())
for file in filelist:
    if os.path.splitext(file)[1] == '.pdf':
        name = os.path.splitext(file)[0]
        p1 = subprocess.Popen(["pdf2ps",file])
        p1.wait()
        print("pdf2ps "+file)
        p2 = subprocess.Popen(["ps2pdf",name+".ps","hack_"+name+".pdf"])
        p2.wait()
        print("ps2pdf "+name+".ps "+"hack_"+name+".pdf")
        print("succeed to trans "+file)
