
``` bash
python tool.py -f 123 -c 10000 direct


fio --filename=./file --direct=1   --rw=randwrite --refill_buffers --norandommap --randrepeat=0 --ioengine=libaio --bs=4k --rwmixread=100 --iodepth=1 --numjobs=1  --group_reporting --name=4ktestwrite --size=20M --runtime=20 --time_based
```



direct大概单进程5000IOPS