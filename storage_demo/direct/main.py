from logger import log
import logging
import os
import mmap

def main_func(file, count, *args, **kwargs):
    log(logging.INFO, "start")
    log(logging.INFO, file)
    # for i in range(count):
    write(file, count)
    log(logging.INFO, "end")


def write(filepath, count):
    log(logging.INFO, f"file: {filepath}")
    # filepath = os.path.join(os.curdir, filepath)
    fd = os.open(filepath, os.O_DIRECT | os.O_WRONLY |os.O_CREAT)
    log(logging.DEBUG, f"fd: {fd}")
    if fd < 0:
        log(logging.ERROR, f"fail to open {filepath}")

    m = mmap.mmap(-1, 4096)
    data = "1"*4096
    buff = data.encode()
    m.write(buff)

    log(logging.DEBUG, f"type: {type(buff)} data type: {type(data)}")
    for i in range(count):
        ret = os.write(fd, m)
    log(logging.INFO, f"os write ret: {ret}")
    os.close(fd)

