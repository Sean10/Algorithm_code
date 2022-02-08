import asyncio
import aiofiles
import time
import logging
from logger import log
import decoration

@decoration.time_count
def main_func(file, count, depth=1, *args, **kwargs):
    """
    pass
    """
    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(True)
    try:
        event_loop.run_until_complete(write(event_loop, file, count, depth))
    finally:
        event_loop.close()

    log(logging.INFO, "end")


async def produce(Q, count, n_jobs):
    """
    produce 
    """
    data = "1"*4096
    cnt = 1
    for i in range(count):
        # await Q.put(data)
        await Q.put(data)
        log(logging.DEBUG, f"produce {cnt}")
        cnt += 1
    for i in range(n_jobs):
        await Q.put(None)
        cnt += 1
        log(logging.DEBUG, f"produce {cnt}")

    # await Q.join()
    log(logging.DEBUG, f"produce exit {cnt}")
    return 0


async def consume(Q, fd):
    """
    consume
    """
    cnt = 1
    while True:
        n = await Q.get()
        log(logging.DEBUG, f"consume {cnt}")
        cnt += 1 
        if n is None:
            Q.task_done()
            log(logging.DEBUG, f"exit consume {cnt}")
            return 
        await fd.write(n)
        Q.task_done()


async def write(loop, file, count, depth=1):
    """
    pass
    """
    Q = asyncio.Queue(maxsize=128)
    fd = await aiofiles.open(file, "w")
    
    consumers = [
        loop.create_task(consume(Q, fd)) for i in range(depth)
    ]

    producers = loop.create_task(produce(Q, count, depth))
    
    await asyncio.wait(consumers+[producers])
    await fd.close()
    # await Q.join()
    # tasks = consumers + [producers]
    # for task in tasks:
    #     task.cancel()
    # await asyncio.gather(*tasks, return_exceptions=True)