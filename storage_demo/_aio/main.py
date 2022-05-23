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
    log(logging.DEBUG, f"callback end")


def get_block(fd, offset):
    cb = libaio.AIOBlock(libaio.AIOBLOCK_MODE_WRITE)
    # event = libaio.EventFD()
    # cb.eventfd = event
    cb.target_file = fd
    cb.onCompletion = lambda block, res, res2: (callback())

    cb.buffer_list = [bytearray("1" * 4096, encoding="utf-8")]
    cb.offset = offset
    return cb


def write(file, count, depth=1):
    """
    pass
    """
    data = "1" * 4096
    fd = open(file, "w")
    ctx = libaio.AIOContext(128)

    for i in range(count // depth):
        buffer_list = []
        for j in range(depth):
            cb = get_block(fd, i * j * 4096)
            buffer_list.append(cb)
        ret = ctx.submit(buffer_list)
        log(logging.DEBUG, f"submit ret: {ret}")

        ret = ctx.getEvents()
        log(logging.DEBUG, f"get events: {ret}")

    ret = ctx.close()
    log(logging.INFO, f"close: {ret}")

    fd.close()
