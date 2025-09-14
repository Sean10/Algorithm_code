


# 单线程性能


编译器优化是性能提升的主要因素（230%提升），而内存管理优化在当前测试场景下作用有限。线程本地缓存版本的真正优势会在以下多线程高并发场景. 后续继续.

## 1. cas.cc

```
g++ -std=c++11 -pthread cas.cc -o a -latomic
perf stat ./a

100000000/24s = 416.6 wops/s

 Performance counter stats for './a':

         24,003.39 msec task-clock                       #    1.840 CPUs utilized
            16,083      context-switches                 #  670.030 /sec
                10      cpu-migrations                   #    0.417 /sec
            58,228      page-faults                      #    2.426 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

      13.043279685 seconds time elapsed


  14.24%  a        a                    [.] _ZN13LockFreeQueueIiE3popERi
  14.24%  a        a                    [.] _ZNSt6atomicIP4NodeIiEE21compare_exchange_weakERS2_S2_St12memory_orderS5_
  13.20%  a        a                    [.] _ZNKSt6atomicIP4NodeIiEE4loadESt12memory_order
  11.14%  a        libc.so.6            [.] _int_malloc
  11.10%  a        libc.so.6            [.] _int_free
   6.71%  a        libc.so.6            [.] malloc
   5.51%  a        a                    [.] _ZNSt6atomicIP4NodeIiEE5storeES2_St12memory_order
   4.39%  a        a                    [.] _ZSt23__is_constant_evaluatedv
   3.57%  a        a                    [.] _ZStanSt12memory_orderSt23__memory_order_modifier
   2.88%  a        a                    [.] _ZN13LockFreeQueueIiE4pushERKi
   2.28%  a        libc.so.6            [.] cfree@GLIBC_2.2.5
   1.81%  a        a                    [.] _ZN4NodeIiEC1ERKi
   1.59%  a        a                    [.] _ZZ4mainENKUlvE0_clEv
   1.29%  a        a                    [.] _ZNSt13__atomic_baseIP4NodeIiEEC1ES2_
   0.82%  a        libstdc++.so.6.0.30  [.] _Znwm
   0.77%  a        a                    [.] _ZNSt6atomicIP4NodeIiEEC2ES2_
   0.65%  a        a                    [.] _ZZ4mainENKUlvE_clEv
   0.47%  a        libc.so.6            [.] malloc_consolidate
   0.22%  a        [kernel.kallsyms]    [k] _raw_spin_unlock_irqrestore
   0.22%  a        [kernel.kallsyms]    [k] do_user_addr_fault
   0.22%  a        [kernel.kallsyms]    [k] mtree_range_walk
```


### -O2

```
[root@VM-16-17-opencloudos lock_free_q]# perf stat time ./a
Producer finished
Consumer finished, processed 100000000 items
All tests passed
12.04user 0.53system 0:07.28elapsed 172%CPU (0avgtext+0avgdata 425780maxresident)k
0inputs+0outputs (0major+105735minor)pagefaults 0swaps

 Performance counter stats for 'time ./a':

         12,631.36 msec task-clock                       #    1.733 CPUs utilized
            13,140      context-switches                 #    1.040 K/sec
                10      cpu-migrations                   #    0.792 /sec
           105,801      page-faults                      #    8.376 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

       7.287710094 seconds time elapsed

      12.043203000 seconds user
       0.539306000 seconds sys

  22.11%  a        libc.so.6            [.] _int_free
  20.96%  a        a                    [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ4mainEUlvE0_EEEEE6_M_runEv
  18.64%  a        libc.so.6            [.] _int_malloc
  11.25%  a        libc.so.6            [.] malloc
   9.94%  a        a                    [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ4mainEUlvE_EEEEE6_M_runEv
   8.63%  a        libc.so.6            [.] cfree@GLIBC_2.2.5
   1.08%  a        libc.so.6            [.] malloc_consolidate
   0.69%  a        libstdc++.so.6.0.30  [.] _Znwm
   0.46%  a        [kernel.kallsyms]    [k] clear_page_erms
   0.46%  a        a                    [.] _ZdlPv@plt
   0.46%  a        libc.so.6            [.] __mprotect
   0.39%  a        libstdc++.so.6.0.30  [.] free@plt
   0.39%  a        libstdc++.so.6.0.30  [.] malloc@plt
   0.31%  a        [kernel.kallsyms]    [k] _raw_spin_unlock_irqrestore
   0.31%  a        [kernel.kallsyms]    [k] do_user_addr_fault
   0.31%  a        [kernel.kallsyms]    [k] exit_to_user_mode_loop
   0.31%  a        [kernel.kallsyms]    [k] finish_task_switch.isra.0
   0.31%  a        libc.so.6            [.] sysmalloc
   0.23%  a        [kernel.kallsyms]    [k] get_mem_cgroup_from_mm
   0.23%  a        a                    [.] _Znwm@plt
   0.15%  a        [kernel.kallsyms]    [k] syscall_enter_from_user_mode
   0.15%  a        libc.so.6            [.] __sched_yield
   0.08%  a        [kernel.kallsyms]    [k] __mem_cgroup_charge
   0.08%  a        [kernel.kallsyms]    [k] __mod_node_page_state
   0.08%  a        [kernel.kallsyms]    [k] __next_zones_zonelist
   0.08%  a        [kernel.kallsyms]    [k] __pte_offset_map
   0.08%  a        [kernel.kallsyms]    [k] __rb_insert_augmented
   0.08%  a        [kernel.kallsyms]    [k] __schedule
   0.08%  a        [kernel.kallsyms]    [k] __slab_free
   0.08%  a        [kernel.kallsyms]    [k] __vm_enough_memory
   0.08%  a        [kernel.kallsyms]    [k] _raw_spin_lock
   0.08%  a        [kernel.kallsyms]    [k] arch_vma_name
   0.08%  a        [kernel.kallsyms]    [k] change_protection_range
   0.08%  a        [kernel.kallsyms]    [k] charge_memcg
   0.08%  a        [kernel.kallsyms]    [k] do_mprotect_pkey
   0.08%  a        [kernel.kallsyms]    [k] down_write
   0.08%  a        [kernel.kallsyms]    [k] down_write_killable
   0.08%  a        [kernel.kallsyms]    [k] free_unref_page_prepare
   0.08%  a        [kernel.kallsyms]    [k] handle_mm_fault
   0.08%  a        [kernel.kallsyms]    [k] mas_walk
   0.08%  a        [kernel.kallsyms]    [k] mas_wr_append
   0.08%  a        [kernel.kallsyms]    [k] mas_wr_end_piv
   0.08%  a        [kernel.kallsyms]    [k] mas_wr_spanning_store.isra.0
   0.08%  a        [kernel.kallsyms]    [k] mtree_range_walk
   0.08%  a        [kernel.kallsyms]    [k] perf_event_mmap

```


## 2. with tcmalloc

```
g++ -std=c++11 -pthread 1.cas.cc -o a -latomic -ltcmalloc
perf stat ./a

100000000/21.1s = 473.9 wops/s

[root@VM-16-17-opencloudos lock_free_q]# perf stat ./a
Producer finished
Consumer finished, processed 100000000 items
All tests passed

 Performance counter stats for './a':

         21,173.49 msec task-clock                       #    1.577 CPUs utilized
            19,625      context-switches                 #  926.866 /sec
                83      cpu-migrations                   #    3.920 /sec
           114,727      page-faults                      #    5.418 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

      13.425633344 seconds time elapsed

      19.901576000 seconds user
       1.214146000 seconds sys

 17.03%  a        a                      [.] _ZNSt6atomicIP4NodeIiEE21compare_exchange_weakERS2_S2_St12memory_orderS5_
  12.55%  a        a                      [.] _ZNKSt6atomicIP4NodeIiEE4loadESt12memory_order
  10.00%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList11InsertRangeEPvS1_i
   7.17%  a        a                      [.] _ZNSt6atomicIP4NodeIiEE5storeES2_St12memory_order
   6.84%  a        a                      [.] _ZN13LockFreeQueueIiE3popERi
   6.18%  a        libc.so.6              [.] syscall
   4.53%  a        a                      [.] _ZSt23__is_constant_evaluatedv
   3.77%  a        a                      [.] _ZN13LockFreeQueueIiE4pushERKi
   3.21%  a        a                      [.] _ZStanSt12memory_orderSt23__memory_order_modifier
   3.07%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList14ReleaseToSpansEPv
   2.55%  a        a                      [.] _ZN4NodeIiEC1ERKi
   2.22%  a        [kernel.kallsyms]      [k] syscall_enter_from_user_mode
   2.12%  a        libtcmalloc.so.4.5.12  [.] tc_newarray
   2.08%  a        a                      [.] _ZNSt13__atomic_baseIP4NodeIiEEC1ES2_
   2.08%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList17FetchFromOneSpansEiPPvS2_
   1.89%  a        libtcmalloc.so.4.5.12  [.] _ZN8SpinLock8SpinLoopEv
   1.51%  a        libtcmalloc.so.4.5.12  [.] tc_deletearray
   0.99%  a        a                      [.] _ZNSt6atomicIP4NodeIiEEC2ES2_
   0.99%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList18ReleaseListToSpansEPv
   0.90%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList11RemoveRangeEPPvS2_i
   0.75%  a        a                      [.] _ZZ4mainENKUlvE0_clEv

```

### -O2

```
All tests passed
8.98user 1.72system 0:07.53elapsed 142%CPU (0avgtext+0avgdata 836084maxresident)k
616inputs+0outputs (5major+208151minor)pagefaults 0swaps

 Performance counter stats for 'time ./a':

         10,742.00 msec task-clock                       #    1.426 CPUs utilized
            10,593      context-switches                 #  986.129 /sec
               148      cpu-migrations                   #   13.778 /sec
           208,222      page-faults                      #   19.384 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

       7.534296773 seconds time elapsed

       8.981854000 seconds user
       1.725271000 seconds sys

  16.74%  a        libc.so.6              [.] syscall
  16.65%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList11InsertRangeEPvS1_i
  11.66%  a        a                      [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ4mainEUlvE0_EEEEE6_M_runEv
  10.45%  a        a                      [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ4mainEUlvE_EEEEE6_M_runEv
   5.46%  a        [kernel.kallsyms]      [k] syscall_enter_from_user_mode
   4.72%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList14ReleaseToSpansEPv
   4.26%  a        libtcmalloc.so.4.5.12  [.] tc_newarray
   3.61%  a        libtcmalloc.so.4.5.12  [.] tc_deletearray
   2.87%  a        libtcmalloc.so.4.5.12  [.] _ZN8SpinLock8SpinLoopEv
   2.22%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList17FetchFromOneSpansEiPPvS2_
   2.13%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList8PopulateEv
   1.57%  a        [kernel.kallsyms]      [k] do_user_addr_fault
   1.57%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList11RemoveRangeEPPvS2_i
   1.30%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList18ReleaseListToSpansEPv
   1.20%  a        [kernel.kallsyms]      [k] clear_page_erms
   1.02%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc11ThreadCache21FetchFromCentralCacheEjiPFPvmE
   0.65%  a        [kernel.kallsyms]      [k] _raw_spin_unlock_irqrestore
   0.65%  a        [kernel.kallsyms]      [k] finish_task_switch.isra.0
   0.65%  a        [kernel.kallsyms]      [k] futex_wake
   0.65%  a        [kernel.kallsyms]      [k] get_futex_key
   0.65%  a        libtcmalloc.so.4.5.12  [.] _ZN4base8internal12SpinLockWakeEPSt6atomicIiEb
   0.65%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList14ReleaseToSpansEPv@plt
   0.56%  a        [kernel.kallsyms]      [k] futex_hash
   0.46%  a        [kernel.kallsyms]      [k] do_futex
   0.37%  a        [kernel.kallsyms]      [k] __raw_callee_save___pv_queued_spin_unlock
   0.37%  a        [kernel.kallsyms]      [k] _raw_spin_lock
   0.37%  a        [kernel.kallsyms]      [k] exit_to_user_mode_loop
   0.37%  a        [kernel.kallsyms]      [k] get_page_from_freelist
   0.37%  a        [kernel.kallsyms]      [k] handle_softirqs
   0.37%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList11InsertRangeEPvS1_i@plt
   0.28%  a        [kernel.kallsyms]      [k] __x64_sys_futex
   0.28%  a        [kernel.kallsyms]      [k] get_mem_cgroup_from_mm
   0.19%  a        [kernel.kallsyms]      [k] __get_user_nocheck_4
   0.19%  a        [kernel.kallsyms]      [k] charge_memcg
   0.19%  a        [kernel.kallsyms]      [k] handle_mm_fault
   0.19%  a        [kernel.kallsyms]      [k] lock_vma_under_rcu
   0.19%  a        [kernel.kallsyms]      [k] try_charge_memcg
   0.19%  a        [kernel.kallsyms]      [k] up_read
   0.19%  a        a                      [.] _ZdlPv@plt
   0.19%  a        libtcmalloc.so.4.5.12  [.] _ZN8SpinLock8SlowLockEv@plt
   0.19%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc15CentralFreeList18ReleaseListToSpansEPv@plt
   0.19%  a        libtcmalloc.so.4.5.12  [.] _ZN8tcmalloc8PageHeap18RemoveFromFreeListEPNS_4SpanE
   0.09%  a        [kernel.kallsyms]      [k] __handle_mm_fault
   0.09%  a        [kernel.kallsyms]      [k] __hrtimer_init
   0.09%  a        [kernel.kallsyms]      [k] __next_zones_zonelist
```


## 3. with thread local cache

```
g++ -std=c++11 -pthread 3.cas_cache_pool.cc -o 3.a -latomic
perf stat ./a

100000000/21.73s = 460.19 wops/s
root@VM-16-17-opencloudos lock_free_q]# perf stat ./b
[root@VM-16-17-opencloudos lock_free_q]# perf stat time ./b
=== 缓存池优化的无锁队列测试 ===

1. 单线程性能测试:
优化版生产者完成
优化版消费者完成，处理了 100000000 个项目
优化版测试通过，耗时: 21715 毫秒
缓存池大小: 1000

2. 多线程压力测试:

所有测试完成！
38.15user 0.58system 0:21.73elapsed 178%CPU (0avgtext+0avgdata 258232maxresident)k
0inputs+0outputs (0major+63837minor)pagefaults 0swaps

 Performance counter stats for 'time ./b':

         38,856.55 msec task-clock                       #    1.788 CPUs utilized
            35,493      context-switches                 #  913.437 /sec
                 8      cpu-migrations                   #    0.206 /sec
            63,905      page-faults                      #    1.645 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

      21.734383496 seconds time elapsed

      38.152751000 seconds user
       0.590132000 seconds sys


  20.36%  b        b                    [.] _ZNSt6atomicIP4NodeIiEE21compare_exchange_weakERS2_S2_St12memory_orderS5_
  13.75%  b        b                    [.] _ZN22OptimizedLockFreeQueueIiE3popERi
  12.95%  b        b                    [.] _ZNKSt6atomicIP4NodeIiEE4loadESt12memory_order
  12.03%  b        b                    [.] _ZNSt6atomicIP4NodeIiEE5storeES2_St12memory_order
   6.17%  b        b                    [.] _ZSt23__is_constant_evaluatedv
   5.32%  b        b                    [.] _ZN8NodePoolIiE7acquireEv
   4.90%  b        b                    [.] _ZStanSt12memory_orderSt23__memory_order_modifier
   4.70%  b        b                    [.] _ZN8NodePoolIiE7releaseEP4NodeIiE
   2.66%  b        b                    [.] _ZN22OptimizedLockFreeQueueIiE4pushERKi
   1.91%  b        b                    [.] _ZN4NodeIiEC1ERKi
   1.83%  b        b                    [.] _ZN16ThreadLocalCacheIiE7acquireEv
   1.32%  b        libc.so.6            [.] _int_malloc
   1.16%  b        b                    [.] _ZN16ThreadLocalCacheIiE12refill_cacheEv
   1.03%  b        libc.so.6            [.] _int_free
   0.90%  b        libc.so.6            [.] malloc
   0.88%  b        b                    [.] _ZNSt6vectorIP4NodeIiESaIS2_EEixEm
   0.83%  b        b                    [.] _ZNSt13__atomic_baseIP4NodeIiEEC1ES2_
   0.83%  b        b                    [.] _ZNSt6atomicIP4NodeIiEEC2ES2_
   0.77%  b        b                    [.] _ZN16ThreadLocalCacheIiE7releaseEP4NodeIiE
   0.57%  b        b                    [.] _ZTWN22OptimizedLockFreeQueueIiE11local_cacheE
   0.52%  b        b                    [.] _ZnwmPv
   0.49%  b        [kernel.kallsyms]    [k] exit_to_user_mode_loop
   0.49%  b        b                    [.] _ZZ16performance_testvENKUlvE0_clEv
   0.44%  b        libc.so.6            [.] __sched_yield
   0.41%  b        [kernel.kallsyms]    [k] __schedule
   0.34%  b        libc.so.6            [.] cfree@GLIBC_2.2.5
   0.31%  b        [kernel.kallsyms]    [k] finish_task_switch.isra.0
   0.28%  b        b                    [.] __tls_init
   0.26%  b        b                    [.] _ZZ16performance_testvENKUlvE_clEv
   0.13%  b        [kernel.kallsyms]    [k] do_user_addr_fault
   0.13%  b        [kernel.kallsyms]    [k] syscall_enter_from_user_mode
   0.13%  b        libstdc++.so.6.0.30  [.] _Znwm
   0.10%  b        b                    [.] _ZN4NodeIiEC1Ev
   0.05%  b        [kernel.kallsyms]    [k] __list_del_entry_valid_or_report
   0.05%  b        [kernel.kallsyms]    [k] _raw_spin_unlock_irqrestore
   0.05%  b        [kernel.kallsyms]    [k] charge_memcg
   0.05%  b        [kernel.kallsyms]    [k] clear_page_erms
   0.05%  b        [kernel.kallsyms]    [k] get_mem_cgroup_from_mm
   0.05%  b        libc.so.6            [.] __mprotect
   0.03%  b        [kernel.kallsyms]    [k] __rcu_read_lock
   0.03%  b        [kernel.kallsyms]    [k] _raw_spin_trylock
   0.03%  b        [kernel.kallsyms]    [k] blkcg_maybe_throttle_current
   0.03%  b        [kernel.kallsyms]    [k] br_nf_post_routing
   0.03%  b        [kernel.kallsyms]    [k] change_pmd_range.isra.0
   0.03%  b        [kernel.kallsyms]    [k] cpu_util.constprop.0

```

### -O2

```
11.94user 0.59system 0:07.59elapsed 165%CPU (0avgtext+0avgdata 547292maxresident)k
0inputs+0outputs (0major+136137minor)pagefaults 0swaps

 Performance counter stats for 'time ./b':

         12,580.18 msec task-clock                       #    1.656 CPUs utilized
             9,408      context-switches                 #  747.843 /sec
                13      cpu-migrations                   #    1.033 /sec
           136,207      page-faults                      #   10.827 K/sec
   <not supported>      cycles
   <not supported>      instructions
   <not supported>      branches
   <not supported>      branch-misses

       7.595540151 seconds time elapsed

      11.951541000 seconds user
       0.594919000 seconds sys


 46.27%  b        b                    [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ16performance_testvEUlvE0_EEEEE6_M_runEv
  29.80%  b        b                    [.] _ZNSt6thread11_State_implINS_8_InvokerISt5tupleIJZ16performance_testvEUlvE_EEEEE6_M_runEv
   5.13%  b        libc.so.6            [.] malloc
   4.80%  b        libc.so.6            [.] _int_malloc
   4.22%  b        libc.so.6            [.] _int_free
   0.99%  b        b                    [.] __tls_init
   0.99%  b        libc.so.6            [.] cfree@GLIBC_2.2.5
   0.83%  b        [kernel.kallsyms]    [k] clear_page_erms
   0.75%  b        [kernel.kallsyms]    [k] do_user_addr_fault
   0.66%  b        [kernel.kallsyms]    [k] _raw_spin_unlock_irqrestore
   0.41%  b        libstdc++.so.6.0.30  [.] _Znwm
   0.25%  b        [kernel.kallsyms]    [k] exit_to_user_mode_loop
   0.25%  b        [kernel.kallsyms]    [k] perf_event_mmap_output
   0.25%  b        [kernel.kallsyms]    [k] try_charge_memcg
   0.25%  b        libc.so.6            [.] __mprotect
   0.17%  b        [kernel.kallsyms]    [k] __rcu_read_lock
   0.17%  b        [kernel.kallsyms]    [k] charge_memcg
   0.17%  b        [kernel.kallsyms]    [k] finish_task_switch.isra.0
   0.17%  b        [kernel.kallsyms]    [k] get_mem_cgroup_from_mm
   0.17%  b        [kernel.kallsyms]    [k] mas_wr_spanning_store.isra.0
   0.17%  b        [kernel.kallsyms]    [k] mtree_range_walk
   0.17%  b        [kernel.kallsyms]    [k] schedule
   0.17%  b        [kernel.kallsyms]    [k] selinux_file_mprotect
   0.17%  b        [kernel.kallsyms]    [k] syscall_enter_from_user_mode
   0.17%  b        b                    [.] _ZdlPv@plt
   0.08%  b        [kernel.kallsyms]    [k] __alloc_pages
   0.08%  b        [kernel.kallsyms]    [k] __call_rcu_common.constprop.0
   0.08%  b        [kernel.kallsyms]    [k] __handle_mm_fault
   0.08%  b        [kernel.kallsyms]    [k] __next_zones_zonelist
   0.08%  b        [kernel.kallsyms]    [k] __slab_free
   0.08%  b        [kernel.kallsyms]    [k] anon_vma_interval_tree_insert
   0.08%  b        [kernel.kallsyms]    [k] avc_lookup
   0.08%  b        [kernel.kallsyms]    [k] change_protection_range
   0.08%  b        [kernel.kallsyms]    [k] change_pte_range
   0.08%  b        [kernel.kallsyms]    [k] do_anonymous_page
   0.08%  b        [kernel.kallsyms]    [k] down_read_trylock
   0.08%  b        [kernel.kallsyms]    [k] handle_softirqs
   0.08%  b        [kernel.kallsyms]    [k] hugepage_vma_check
   0.08%  b        [kernel.kallsyms]    [k] kmem_cache_free
   0.08%  b        [kernel.kallsyms]    [k] kmem_cache_free_bulk.part.0
   0.08%  b        [kernel.kallsyms]    [k] mas_spanning_rebalance.isra.0
   0.08%  b        [kernel.kallsyms]    [k] mas_topiary_replace
   0.08%  b        [kernel.kallsyms]    [k] mas_walk
   0.08%  b        [kernel.kallsyms]    [k] memcpy_orig
   0.08%  b        [kernel.kallsyms]    [k] mod_objcg_state

```