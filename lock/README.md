

# 编译互斥锁示例
clang++ demo_mutex.cc -std=c++11 -stdlib=libc++

# 编译锁性能对比示例

适用openEuler/centos x86架构环境

g++ lock_benchmark.cc -std=c++11 -stdlib=libc++ -o lock_benchmark

# 对比测试：
线程数：4
每个线程循环次数：100000
测量指标：
计数器最终值（验证正确性）
每次加锁操作的平均延迟（微秒）
运行程序后，你可以看到两种锁的性能对比。一般来说：
自旋锁在临界区很小且竞争不激烈时性能更好
互斥锁在临界区较大或竞争激烈时更适合，因为它会让出 CPU
你可以通过调整 NUM_THREADS 和 ITERATIONS 来测试不同场景下的性能表现。

## 运行结果

```
CPU核心数: 4

=== 测试场景 ===
线程数: 4
每线程迭代次数: 10000
持锁时间: 0 微秒

互斥锁结果 (持锁时间: 0微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 0.20555 微秒
- 每秒操作次数: 4.86499e+06

自旋锁结果 (持锁时间: 0微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 0.17449 微秒
- 每秒操作次数: 5.73099e+06


=== 测试场景 ===
线程数: 4
每线程迭代次数: 10000
持锁时间: 1 微秒

互斥锁结果 (持锁时间: 1微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 7.42157 微秒
- 每秒操作次数: 134742

自旋锁结果 (持锁时间: 1微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 4.63311 微秒
- 每秒操作次数: 215838


=== 测试场景 ===
线程数: 4
每线程迭代次数: 10000
持锁时间: 10 微秒

互斥锁结果 (持锁时间: 10微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 46.3798 微秒
- 每秒操作次数: 21561.1

自旋锁结果 (持锁时间: 10微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 40.7026 微秒
- 每秒操作次数: 24568.4


=== 测试场景 ===
线程数: 4
每线程迭代次数: 10000
持锁时间: 100 微秒

互斥锁结果 (持锁时间: 100微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 358.141 微秒
- 每秒操作次数: 2792.2

自旋锁结果 (持锁时间: 100微秒):
- 最终计数器值: 40000
- 平均每次加锁操作延迟: 400.63 微秒
- 每秒操作次数: 2496.07
```

# 编译死锁测试程序
g++ mutex_deadlock.cc -std=c++11 -pthread -g -o mutex_deadlock
g++ spinlock_deadlock.cc -std=c++11 -pthread -g -o spinlock_deadlock

# 运行 perf 分析

```
perf top -p $(pgrep mutex_deadlock)
perf top -p $(pgrep spinlock_deadlock)
```


### 死锁时观察perf现象

#### spinlock

```

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                                                                              
3425891 root      20   0  101004   1936   1752 S 199.3   0.1   3:24.74 spinlock_deadlo   

Samples: 25K of event 'cpu-clock:pppH', Event count (approx.): 6394250000
Overhead  Command          Shared Object      Symbol
  99.97%  spinlock_deadlo  spinlock_deadlock  [.] SpinLock::lock
   0.00%  spinlock_deadlo  [kernel.kallsyms]  [k] __do_page_fault
   0.00%  spinlock_deadlo  [kernel.kallsyms]  [k] native_write_msr
   0.00%  spinlock_deadlo  [kernel.kallsyms]  [k] perf_event_mmap
   0.00%  spinlock_deadlo  [kernel.kallsyms]  [k] queue_work_on
   0.00%  spinlock_deadlo  ld-2.28.so         [.] _dl_lookup_symbol_x
   0.00%  spinlock_deadlo  ld-2.28.so         [.] _dl_relocate_object
   0.00%  spinlock_deadlo  ld-2.28.so         [.] do_lookup_x
```

#### mutex

```
3428084 root      20   0  101004   1976   1792 S   0.0   0.1   0:00.00 mutex_deadlock         

Samples: 5  of event 'cpu-clock:pppH', Event count (approx.): 1250000
Overhead  Command         Shared Object      Symbol
  40.00%  mutex_deadlock  ld-2.28.so         [.] do_lookup_x
  20.00%  mutex_deadlock  [kernel.kallsyms]  [k] pfn_pte
  20.00%  mutex_deadlock  [kernel.kallsyms]  [k] unmapped_area_topdown
  20.00%  mutex_deadlock  ld-2.28.so         [.] _dl_lookup_symbol_x

[root@VM-16-11-centos ~]# strace -fp 3428084
strace: Process 3428084 attached with 3 threads
[pid 3428086] futex(0x6021a0, FUTEX_WAIT_PRIVATE, 2, NULL <unfinished ...>
[pid 3428085] futex(0x6021e0, FUTEX_WAIT_PRIVATE, 2, NULL <unfinished ...>
[pid 3428084] futex(0x7f62483cd9d0, FUTEX_WAIT, 3428085, NULL^Cstrace: Process 3428084 detached
 <detached ...>
strace: Process 3428085 detached
```
