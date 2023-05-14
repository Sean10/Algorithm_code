from contextlib import contextmanager
import faulthandler
import traceback
import syslog
import sys

@contextmanager
def ignored(*exceptions):
        try:
                fd = open("/var/log/ceph/ceph_segfault.log", "a+")
                faulthandler.enable(fd)
                yield
        except Exception as e:
                syslog.syslog(traceback.format_exc())
                raise
        finally:
                fd.close()




with ignored(Exception):
	# simulate segfault
	import ctypes
        ctypes.string_at(0)
    # simulate exception
    # xxx

