import libaio
import time
import logging
from logger import log
import decoration

@decoration.time_count
def main_func(file, count, depth=1, *args, **kwargs):
    """
    pass
    """

    write(file, count, depth)
    log(logging.INFO, "end")

def callback():
    log(logging.INFO, f"callback end")

def get_block(fd):
    cb = libaio.AIOBlock(libaio.AIOBLOCK_MODE_WRITE)
    # event = libaio.EventFD()
    # cb.eventfd = event
    cb.target_file = fd
    cb.onCompletion = lambda block, res, res2: (callback())

    cb.buffer_list = [bytearray("1"*4096, encoding="utf-8")]
    cb.offset = 0
    return cb

def write(file, count, depth=1):
    """
    pass
    """
    data = "1"*4096
    fd = open(file, "w")
    ctx = libaio.AIOContext(128)  

    for i in range(count):
        cb = get_block(fd)
        ret = ctx.submit([cb])
        log(logging.INFO, f"submit ret: {ret}")

        ret = ctx.getEvents()
        log(logging.INFO, f"get events: {ret}")

    ret = ctx.close()
    log(logging.INFO, f"close: {ret}")
    
    fd.close()
