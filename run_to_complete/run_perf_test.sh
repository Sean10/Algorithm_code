#!/bin/bash

# 清理并重新编译项目
rm -rf build
mkdir -p build
cd build
cmake ..
make

echo "=================== CPU性能测试开始 ==================="

# 创建结果目录
mkdir -p results

echo "------------------- RTC实现测试 -------------------"
# 使用time获取基础执行时间
echo "基础时间测试..."
/usr/bin/time -v ./rtc_demo 2> results/rtc_time.txt

# 使用top获取CPU使用情况
echo "CPU使用率测试(10次采样)..."
for i in {1..10}; do
    top -b -n 1 -p $$ >> results/rtc_top.txt
    ./rtc_demo
    sleep 0.1
done

# 使用ps获取进程状态
echo "进程状态采样..."
for i in {1..10}; do
    ps -o pid,ppid,pcpu,pmem,vsz,rss,cmd -p $$ >> results/rtc_ps.txt
    ./rtc_demo
    sleep 0.1
done

echo -e "\n------------------- 传统实现测试 -------------------"
# 对传统实现进行相同的测试
echo "基础时间测试..."
/usr/bin/time -v ./traditional_demo 2> results/traditional_time.txt

echo "CPU使用率测试(10次采样)..."
for i in {1..10}; do
    top -b -n 1 -p $$ >> results/traditional_top.txt
    ./traditional_demo
    sleep 0.1
done

echo "进程状态采样..."
for i in {1..10}; do
    ps -o pid,ppid,pcpu,pmem,vsz,rss,cmd -p $$ >> results/traditional_ps.txt
    ./traditional_demo
    sleep 0.1
done

echo "=================== 性能测试完成 ==================="

# 生成性能报告
echo -e "\n生成性能报告..."
echo "CPU性能测试报告" > perf_report.txt
echo "测试时间: $(date)" >> perf_report.txt

echo -e "\n1. 执行时间统计" >> perf_report.txt
echo "RTC实现:" >> perf_report.txt
grep "User time" results/rtc_time.txt >> perf_report.txt
grep "System time" results/rtc_time.txt >> perf_report.txt
grep "Elapsed" results/rtc_time.txt >> perf_report.txt
echo "传统实现:" >> perf_report.txt
grep "User time" results/traditional_time.txt >> perf_report.txt
grep "System time" results/traditional_time.txt >> perf_report.txt
grep "Elapsed" results/traditional_time.txt >> perf_report.txt

echo -e "\n2. 内存使用统计" >> perf_report.txt
echo "RTC实现:" >> perf_report.txt
grep "Maximum resident set size" results/rtc_time.txt >> perf_report.txt
echo "传统实现:" >> perf_report.txt
grep "Maximum resident set size" results/traditional_time.txt >> perf_report.txt

echo -e "\n3. CPU使用率统计(ps)" >> perf_report.txt
echo "RTC实现平均CPU使用率:" >> perf_report.txt
awk '{ sum += $3 } END { print sum/NR "%" }' results/rtc_ps.txt >> perf_report.txt
echo "传统实现平均CPU使用率:" >> perf_report.txt
awk '{ sum += $3 } END { print sum/NR "%" }' results/traditional_ps.txt >> perf_report.txt

echo -e "\n4. 内存使用率统计(ps)" >> perf_report.txt
echo "RTC实现平均内存使用率:" >> perf_report.txt
awk '{ sum += $4 } END { print sum/NR "%" }' results/rtc_ps.txt >> perf_report.txt
echo "传统实现平均内存使用率:" >> perf_report.txt
awk '{ sum += $4 } END { print sum/NR "%" }' results/traditional_ps.txt >> perf_report.txt

# 清理临时文件
rm -rf results

echo "性能报告已生成: perf_report.txt" 
