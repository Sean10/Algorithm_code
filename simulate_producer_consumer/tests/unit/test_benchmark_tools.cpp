#include <gtest/gtest.h>
#include <fstream>
#include <sstream>
#include <cstdio>
#include "tools/csv_writer.hpp"

using namespace bench_tools;

class CSVWriterTest : public ::testing::Test {
protected:
    void SetUp() override {
        latency_file = "test_latency.csv";
        summary_file = "test_summary.csv";
        
        // 清理可能存在的测试文件
        std::remove(latency_file.c_str());
        std::remove(summary_file.c_str());
    }
    
    void TearDown() override {
        // 清理测试文件
        std::remove(latency_file.c_str());
        std::remove(summary_file.c_str());
    }
    
    std::string readFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            return "";
        }
        std::stringstream buffer;
        buffer << file.rdbuf();
        return buffer.str();
    }
    
    std::string latency_file;
    std::string summary_file;
};

TEST_F(CSVWriterTest, LatencyCSVBasic) {
    const int consumer_count = 2;
    const int test_count = 3;
    
    // 创建测试数据
    double** all_latencies = new double*[consumer_count];
    for (int i = 0; i < consumer_count; ++i) {
        all_latencies[i] = new double[test_count];
        for (int j = 0; j < test_count; ++j) {
            all_latencies[i][j] = i * test_count + j + 1.5; // 1.5, 2.5, 3.5, 4.5, 5.5, 6.5
        }
    }
    
    // 写入CSV
    append_latency_csv(latency_file.c_str(), "test_queue", consumer_count, test_count, all_latencies);
    
    // 验证文件内容
    std::string content = readFile(latency_file);
    EXPECT_FALSE(content.empty());
    
    // 检查标题行
    EXPECT_NE(content.find("queue_type,consumer_id,sample_idx,latency_us"), std::string::npos);
    
    // 检查数据行
    EXPECT_NE(content.find("test_queue,0,0,1.500000"), std::string::npos);
    EXPECT_NE(content.find("test_queue,1,2,6.500000"), std::string::npos);
    
    // 清理内存
    for (int i = 0; i < consumer_count; ++i) {
        delete[] all_latencies[i];
    }
    delete[] all_latencies;
}

TEST_F(CSVWriterTest, LatencyCSVWithInvalidData) {
    const int consumer_count = 2;
    const int test_count = 3;
    
    // 创建包含无效数据的测试数据
    double** all_latencies = new double*[consumer_count];
    for (int i = 0; i < consumer_count; ++i) {
        all_latencies[i] = new double[test_count];
        for (int j = 0; j < test_count; ++j) {
            if (i == 0 && j == 1) {
                all_latencies[i][j] = -1.0; // 无效数据
            } else {
                all_latencies[i][j] = i * test_count + j + 1.0;
            }
        }
    }
    
    // 写入CSV
    append_latency_csv(latency_file.c_str(), "test_queue", consumer_count, test_count, all_latencies);
    
    // 验证文件内容
    std::string content = readFile(latency_file);
    
    // 检查有效数据存在
    EXPECT_NE(content.find("test_queue,0,0,1.000000"), std::string::npos);
    EXPECT_NE(content.find("test_queue,1,2,6.000000"), std::string::npos);
    
    // 检查无效数据被跳过
    EXPECT_EQ(content.find("test_queue,0,1,-1.000000"), std::string::npos);
    
    // 清理内存
    for (int i = 0; i < consumer_count; ++i) {
        delete[] all_latencies[i];
    }
    delete[] all_latencies;
}

TEST_F(CSVWriterTest, SummaryCSVBasic) {
    // 写入汇总数据
    append_summary_csv(summary_file.c_str(), "mutex", 4096, 1000, 8, 15, 
                      8000, 1.234567, 0.1, 10.5);
    
    // 验证文件内容
    std::string content = readFile(summary_file);
    EXPECT_FALSE(content.empty());
    
    // 检查标题行
    EXPECT_NE(content.find("queue_type,queue_size,test_count,consumers,timeout_s,total_samples,avg_latency_us,min_latency_us,max_latency_us,throughput_est"), std::string::npos);
    
    // 检查数据行
    EXPECT_NE(content.find("mutex,4096,1000,8,15,8000,1.234567,0.100000,10.500000"), std::string::npos);
}

TEST_F(CSVWriterTest, MultipleAppends) {
    // 第一次写入
    append_summary_csv(summary_file.c_str(), "mutex", 4096, 1000, 8, 15, 
                      8000, 1.234567, 0.1, 10.5);
    
    // 第二次写入（应该追加，不应该重复标题）
    append_summary_csv(summary_file.c_str(), "lockfree", 4096, 1000, 8, 15, 
                      8000, 0.5, 0.05, 2.0);
    
    // 验证文件内容
    std::string content = readFile(summary_file);
    
    // 应该只有一个标题行
    size_t first_header = content.find("queue_type,queue_size");
    size_t second_header = content.find("queue_type,queue_size", first_header + 1);
    EXPECT_EQ(second_header, std::string::npos);
    
    // 应该有两行数据
    EXPECT_NE(content.find("mutex,4096"), std::string::npos);
    EXPECT_NE(content.find("lockfree,4096"), std::string::npos);
}

TEST_F(CSVWriterTest, NullPathHandling) {
    // 测试NULL路径的处理
    double* dummy_latencies[1] = {nullptr};
    
    // 这些调用不应该崩溃
    append_latency_csv(nullptr, "test", 0, 0, dummy_latencies);
    append_latency_csv("", "test", 0, 0, dummy_latencies);
    append_summary_csv(nullptr, "test", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0);
    append_summary_csv("", "test", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0);
    
    // 文件不应该被创建
    EXPECT_TRUE(readFile(latency_file).empty());
    EXPECT_TRUE(readFile(summary_file).empty());
}

TEST_F(CSVWriterTest, ThroughputCalculation) {
    // 测试吞吐量计算
    append_summary_csv(summary_file.c_str(), "test", 1000, 100, 4, 10, 
                      400, 2.0, 1.0, 5.0); // 2微秒平均延迟，4个消费者
    
    std::string content = readFile(summary_file);
    
    // 预期吞吐量 = 1000000/2 * 4 = 2000000
    EXPECT_NE(content.find("2000000.000000"), std::string::npos);
    
    // 测试零延迟的情况
    std::remove(summary_file.c_str());
    append_summary_csv(summary_file.c_str(), "test", 1000, 100, 4, 10, 
                      400, 0.0, 0.0, 0.0); // 零延迟
    
    content = readFile(summary_file);
    EXPECT_NE(content.find("0.000000"), std::string::npos); // 吞吐量应该是0
}
