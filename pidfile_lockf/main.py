# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import fcntl
import sys
import struct
# import errno
import os

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        sys.exit(1)
    task = sys.argv[1]
    task_start_map = {
        "hello": 10,
        "new": 0
    }

    print(os.getpid())
    with open("{}_file.pid", "ab+") as f:
        # f.write('0')
        # f.seek(task_start_map[task])
        try:
            rv = fcntl.lockf(f, fcntl.LOCK_EX, 5, task_start_map[task])
            # time.sleep(20)

        except OSError as e:
            print("fail to lock task :{} e: {} error: {}".format(task, str(e), os.strerror(e.errno)))
            raise(e)
            sys.exit(1)
        print("succeed")
        import time

        time.sleep(150)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
