"""
rbd基础库
"""
from multiprocessing import Pool
import queue
import rados
import rbd

import decoration
from logger import log
from common import *
import random
import numpy as np

CNT = 0

def generate_random_list(upper, count):
    # list=[random.randint(0,upper) for i in range(count)]
    testcase = np.random.randint(0, upper, count)
    return list(testcase)

class IOMethod:
    def __init__(self, pool, conf="./ceph.conf"):
        log(msg=f"init IOMethod, pool: {pool}, conf: {conf}")
        self.rados_inst = rados.Rados(conffile=conf, conf={"rados_mon_op_timeout": "60", "rados_osd_op_timeout": "60", "client_mount_timeout": "60"})
        self.rados_inst.connect()
        self.ioctx = self.rados_inst.open_ioctx(pool)

    def __del__(self):
        self.ioctx.close()
        self.rados_inst.shutdown()

    # @decoration.time_count
    def read(self, image, count, depth=1):
        log(msg="init read")
        with rbd.Image(self.ioctx, image) as image_inst:
            for i in range(count):
                #     image.write(data.encode(), i * 4096)
                data2 = image_inst.read(i * 4096, 4096, )

    def on_complete(self):
        global CNT
        CNT = CNT + 1
        print("complete: ", CNT)
        return 0
    

    @decoration.time_count
    def aio_read(self, image, count, depth=1):
        retval = [None]
        q = queue.Queue(maxsize=depth)

        def cb(comp, buff):
            retval[0] = comp.get_return_value()
        
        
        # rbd_inst = rbd.RBD()
        with rbd.Image(self.ioctx, image) as image_inst:
            size = image_inst.size()
            object_size = 4*1024*1024
            upper_limit = size // object_size
            
            testcase_array = generate_random_list(upper_limit, count)
            log(msg=f"head : {testcase_array[:100]}")
            for i in range(count):
                if q.full():
                    comp = q.get()
                    comp.wait_for_complete_and_cb()
                else:
                # for j in range(depth):
                    comp = image_inst.aio_read(testcase_array[i] * 4096*4096, 4096, cb)
                    q.put(comp)

                # while not q.empty():
            while not q.empty():
                comp = q.get()
                comp.wait_for_complete_and_cb()       

                # completion.wait_for_complete_and_cb()

        # global CNT
        # while cnt < count - 1:
        #     time.sleep(0.01)
        #     if cnt < count -10:
        #         print(cnt)
    # def write(self, file, count, depth=1):
        
    #     data = "1" * 4096

    #     # rbd_inst = rbd.RBD()
    #     with rbd.Image(self.ioctx, "wc1") as image:
    #         for i in range(count):
    #             image.write(data.encode(), i * 4096)
    #     ioctx.close()
    #     rados_inst.shutdown()

    # def on_complete(self):
    #     global CNT
    #     CNT = CNT + 1
    #     print("complete: ", CNT)
    #     return 0

    # def write_depth(self, file, count, depth=1):
    #     rados_inst = rados.Rados(conffile="/etc/ceph/ceph.conf")
    #     rados_inst.connect()

    #     ioctx = rados_inst.open_ioctx("ssd")
    #     data = "1" * 4096
    #     retval = [None]
    #     q = queue.Queue(maxsize=depth)

    #     def cb(comp):
    #         retval[0] = comp.get_return_value()

    #     # rbd_inst = rbd.RBD()
    #     with rbd.Image(ioctx, "rbd0") as image:
    #         for i in range(count // depth):
    #             for j in range(depth):
    #                 comp = image.aio_write(data.encode(), i * 4096, cb)
    #                 q.put(comp)

    #             while not q.empty():
    #                 comp = q.get()
    #                 comp.wait_for_complete_and_cb()

    #             # completion.wait_for_complete_and_cb()

    #     global CNT
    #     # while cnt < count - 1:
    #     #     time.sleep(0.01)
    #     #     if cnt < count -10:
    #     #         print(cnt)
    #     ioctx.close()
    #     rados_inst.shutdown()

def prepare_hash_map_osd():
    """
    目标是计算出只落到指定的osd上的对象名, 然后根据rbd的offset再随机生成访问序列, 即需要一个producer. 

    """
    pass

def init_io(pool, conf, io_type, image, count, depth):
    inst = IOMethod(pool=pool, conf=conf)
    if hasattr(inst, io_type):
        func = getattr(inst, io_type)
        func(image, count , depth)
    else:
        log(logging.ERROR, "no such io_type, only allowed read / write")
        raise ParameterException(msg="no such io_type, only allowed read / write")

def callback(v):
    log(msg=f"hello, {v}")

@decoration.time_count
def main_func(count, pool, conf, image, io_type, depth, image_count, *args, **kwargs):
    """_summary_
    
    Args:
            file (_type_): _description_
            count (_type_): _description_
            depth (int, optional): _description_. Defaults to 1.
    """

    pool_inst = Pool(processes = image_count)
    # init_io(pool,conf,io_type, image, count, depth,)
    for i in range(image_count):
        image_name = f"{image}{i}"
        pool_inst.apply_async(init_io, (pool,conf,io_type, image_name, count, depth,), callback=callback)
    pool_inst.close()
    pool_inst.join()
    # write(file, count, depth)
#     write_depth(file, count, depth)
