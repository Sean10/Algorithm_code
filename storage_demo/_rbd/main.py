from logger import log
import decoration
import argparse
import queue
import rados
import rbd
import time

cnt = 0

def write(file, count, depth=1):
    rados_inst = rados.Rados(conffile="/etc/ceph/ceph.conf")
    rados_inst.connect()

    ioctx = rados_inst.open_ioctx("ssd")
    data = "1"*4096
    
    # rbd_inst = rbd.RBD()
    with rbd.Image(ioctx, "rbd0") as image:
        for i in range(count):
            image.write(data.encode(), i*4096)
    ioctx.close()
    rados_inst.shutdown()

def on_complete():
    global cnt
    cnt = cnt + 1
    print("complete: ", cnt)
    return 0


def write_depth(file, count, depth=1):
    rados_inst = rados.Rados(conffile="/etc/ceph/ceph.conf")
    rados_inst.connect()

    ioctx = rados_inst.open_ioctx("ssd")
    data = "1"*4096
    retval = [None]
    q = queue.Queue(maxsize=depth)

    def cb(comp):
        retval[0] = comp.get_return_value()

    # rbd_inst = rbd.RBD()
    with rbd.Image(ioctx, "rbd0") as image:
        for i in range(count//depth):
            for j in range(depth):
                comp = image.aio_write(data.encode(), i*4096, cb)
                q.put(comp)

            while not q.empty():
                comp = q.get()
                comp.wait_for_complete_and_cb()
            
            # completion.wait_for_complete_and_cb()



    global cnt
    # while cnt < count - 1:
    #     time.sleep(0.01)
    #     if cnt < count -10:
    #         print(cnt)
    ioctx.close()
    rados_inst.shutdown()

@decoration.time_count
def main_func(file, count, depth=1, *args, **kwargs):
    # write(file, count, depth)
    write_depth(file, count, depth)