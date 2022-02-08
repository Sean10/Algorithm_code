
``` bash

echo 0 > /proc/sys/vm/dirty_ratio 
echo 0 > /proc/sys/vm/dirty_background_ratio 

python /workspaces/Algorithm_code/storage_demo/tool.py -f 123 -c 10000 direct


fio --filename=./file --direct=1   --rw=randwrite --refill_buffers --norandommap --randrepeat=0 --ioengine=libaio --bs=4k --rwmixread=100 --iodepth=1 --numjobs=1  --group_reporting --name=4ktestwrite --size=20M --runtime=20 --time_based
```



direct大概单进程5000IOPS



# 测试结果
## 背景
### 延时控制基本相近状态


## fio aio 4K 1depth
### 结果  10.9K IOPS 89us T99 3.8us T999 36 us 

```
$ fio --filename=./file --direct=1   --rw=randwrite --refill_buffers --norandommap --randrepeat=0 --ioengine=libaio --bs=4k --rwmixread=100 --iodepth=1 --numjobs=1  --gro
up_reporting --name=4ktestwrite --size=20M --runtime=20 --time_based                                                                                                               
4ktestwrite: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=1
fio-3.25                                                                                 
Starting 1 process         
Jobs: 1 (f=1): [w(1)][100.0%][w=37.9MiB/s][w=9691 IOPS][eta 00m:00s]
4ktestwrite: (groupid=0, jobs=1): err= 0: pid=1297: Tue Feb  8 02:49:53 2022
  write: IOPS=10.9k, BW=42.7MiB/s (44.8MB/s)(854MiB/20001msec); 0 zone resets
    slat (usec): min=37, max=100789, avg=87.28, stdev=413.99                  
    clat (nsec): min=1176, max=303429, avg=1714.11, stdev=2472.28              
     lat (usec): min=38, max=100834, avg=89.35, stdev=414.14                   
    clat percentiles (nsec):                                                             
     |  1.00th=[ 1240],  5.00th=[ 1272], 10.00th=[ 1288], 20.00th=[ 1304],
     | 30.00th=[ 1304], 40.00th=[ 1320], 50.00th=[ 1352], 60.00th=[ 1496],
     | 70.00th=[ 1768], 80.00th=[ 1816], 90.00th=[ 1960], 95.00th=[ 2224],
     | 99.00th=[ 3824], 99.50th=[ 9280], 99.90th=[36608], 99.95th=[50944],                                                                                                         
     | 99.99th=[72192]
   bw (  KiB/s): min=23144, max=54728, per=100.00%, avg=43860.13, stdev=8867.41, samples=39
   iops        : min= 5786, max=13682, avg=10965.03, stdev=2216.85, samples=39
  lat (usec)   : 2=91.23%, 4=7.82%, 10=0.47%, 20=0.11%, 50=0.32%
  lat (usec)   : 100=0.05%, 250=0.01%, 500=0.01%
  cpu          : usr=5.70%, sys=41.65%, ctx=214776, majf=0, minf=12
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=0,218627,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
  WRITE: bw=42.7MiB/s (44.8MB/s), 42.7MiB/s-42.7MiB/s (44.8MB/s-44.8MB/s), io=854MiB (895MB), run=20001-20001msec
```

## fio aio 4K 8depth
### 12.1k IOPS 660us T99 988 us T999 1.7ms
```
$ fio --filename=./file --direct=1   --rw=randwrite --refill_buffers --norandommap --randrepeat=0 --ioengine=libaio --bs=4k --rwmixread=100 --iodepth=8 --numjobs=1  --gro
up_reporting --name=4ktestwrite --size=20M --runtime=20 --time_based
4ktestwrite: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=8
fio-3.25
Starting 1 process
Jobs: 1 (f=1): [w(1)][95.0%][w=46.6MiB/s][w=11.9k IOPS][eta 00m:01s]
Jobs: 1 (f=1): [w(1)][100.0%][w=48.1MiB/s][w=12.3k IOPS][eta 00m:00s]
4ktestwrite: (groupid=0, jobs=1): err= 0: pid=1408: Tue Feb  8 02:50:40 2022
  write: IOPS=12.1k, BW=47.2MiB/s (49.5MB/s)(943MiB/20001msec); 0 zone resets
    slat (usec): min=37, max=275452, avg=78.92, stdev=670.55
    clat (usec): min=2, max=276276, avg=581.14, stdev=1782.05
     lat (usec): min=71, max=276364, avg=660.35, stdev=1905.94
    clat percentiles (usec):
     |  1.00th=[  453],  5.00th=[  469], 10.00th=[  474], 20.00th=[  486],
     | 30.00th=[  502], 40.00th=[  515], 50.00th=[  529], 60.00th=[  545],
     | 70.00th=[  562], 80.00th=[  603], 90.00th=[  685], 95.00th=[  766],
     | 99.00th=[  988], 99.50th=[ 1090], 99.90th=[ 1745], 99.95th=[ 2737],
     | 99.99th=[84411]
   bw (  KiB/s): min=20490, max=53944, per=100.00%, avg=48321.69, stdev=6347.22, samples=39
   iops        : min= 5122, max=13486, avg=12080.38, stdev=1586.86, samples=39
  lat (usec)   : 4=0.01%, 100=0.01%, 250=0.01%, 500=29.64%, 750=64.70%
  lat (usec)   : 1000=4.76%
  lat (msec)   : 2=0.82%, 4=0.03%, 10=0.01%, 20=0.01%, 50=0.01%
  lat (msec)   : 100=0.01%, 500=0.01%
  cpu          : usr=4.10%, sys=47.60%, ctx=234365, majf=0, minf=12
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=100.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.1%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=0,241505,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=8

Run status group 0 (all jobs):
  WRITE: bw=47.2MiB/s (49.5MB/s), 47.2MiB/s-47.2MiB/s (49.5MB/s-49.5MB/s), io=943MiB (989MB), run=20001-20001msec
```

## sync 1 depth
### 9445 IOPS  105 us
count lat: 0.00011623454093933106 IOPS: 8603.29461379258
count lat: 0.00010586604277292887 IOPS: 9445.899495316842


## async 
### 973 IOPS 1ms
count lat: 0.0010273627167000086 IOPS: 973.3660602480296

## aio 1 depth
### 7298 IOPS 137 uss 
0.00013700544140010608 IOPS: 7298.980170281221

## aio 8 depth
### 1W IOPS 98us
count lat: 9.895054289954714e-05 IOPS: 10106.058751139773 