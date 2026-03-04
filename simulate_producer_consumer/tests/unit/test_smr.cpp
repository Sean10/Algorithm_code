#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <random>
#include <set>

#include "../../src/stage4_smr/hazard_pointers.hpp"
#include "../../src/stage4_smr/epoch_based_reclamation.hpp"

using namespace stage4;

/**
 * Stage4 安全内存回收 (SMR) 机制测试
 * 
 * 测试内容：
 * 1. Hazard Pointers 基本功能测试
 * 2. Epoch-based Reclamation 基本功能测试
 * 3. 内存安全性测试
 * 4. 并发安全性测试
 * 5. 性能对比测试
 */

class SMRTest : public ::testing::Test {
protected:
    static constexpr int TEST_ITERATIONS = 1000;
    static constexpr int THREAD_COUNT = 4;
    
    void SetUp() override {
        // 每个测试前的设置
    }
    
    void TearDown() override {
        // 每个测试后的清理
        DefaultHazardPointers::force_gc();
        DefaultEBR::force_reclaim();
        
        // 清理线程本地状态
        DefaultHazardPointers::thread_exit();
        DefaultEBR::thread_exit();
    }
};

/**
 * Hazard Pointers 基本功能测试
 */
TEST_F(SMRTest, HazardPointersBasic) {
    struct TestNode {
        std::atomic<int> value;
        std::atomic<TestNode*> next;
        
        TestNode(int v = 0) : value(v), next(nullptr) {}
    };
    
    // 测试危险指针保护
    {
        auto* node = new TestNode(42);
        std::atomic<TestNode*> node_ptr{node};
        
        DefaultHazardPointers::HazardGuard<TestNode> guard;
        TestNode* protected_ptr = guard.protect(node_ptr);
        
        EXPECT_EQ(protected_ptr, node);
        EXPECT_EQ(protected_ptr->value.load(), 42);
        
        // 退休节点
        DefaultHazardPointers::retire(node);
        
        // 在保护期间，节点不应该被删除
        // 这里我们无法直接验证，但可以检查统计信息
        auto stats = DefaultHazardPointers::get_statistics();
        EXPECT_GT(stats.total_hazards, 0);
        
        // 清除保护后，强制 GC
        guard.clear_protection();
    }
    
    DefaultHazardPointers::force_gc();
}

TEST_F(SMRTest, HazardPointersMultipleProtection) {
    struct TestNode {
        int value;
        std::atomic<TestNode*> next;
        
        TestNode(int v) : value(v), next(nullptr) {}
    };
    
    // 创建一个链表
    std::vector<TestNode*> nodes;
    for (int i = 0; i < 5; ++i) {
        nodes.push_back(new TestNode(i));
        if (i > 0) {
            nodes[i-1]->next.store(nodes[i]);
        }
    }
    
    std::atomic<TestNode*> head{nodes[0]};
    
    // 使用多个危险指针保护链表遍历
    {
        DefaultHazardPointers::HazardGuard<TestNode> current_guard(0);
        DefaultHazardPointers::HazardGuard<TestNode> next_guard(1);
        
        TestNode* current = current_guard.protect(head);
        EXPECT_NE(current, nullptr);
        EXPECT_EQ(current->value, 0);
        
        int expected_value = 0;
        while (current != nullptr) {
            EXPECT_EQ(current->value, expected_value++);
            
            TestNode* next = next_guard.protect(current->next);
            current_guard.set_protection(next);
            current = next;
        }
    }
    
    // 清理
    for (auto* node : nodes) {
        DefaultHazardPointers::retire(node);
    }
    DefaultHazardPointers::force_gc();
}

/**
 * Epoch-based Reclamation 基本功能测试
 */
TEST_F(SMRTest, EpochBasedReclamationBasic) {
    struct TestNode {
        int value;
        
        TestNode(int v) : value(v) {}
    };
    
    // 测试基本的延迟回收
    {
        DefaultEBR::EpochGuard guard;
        
        auto* node = new TestNode(123);
        EXPECT_EQ(node->value, 123);
        
        // 延迟回收
        DefaultEBR::defer_reclamation(node);
        
        // 在当前纪元内，对象应该还存在
        auto stats = DefaultEBR::get_statistics();
        EXPECT_GT(stats.deferred_objects, 0);
    }
    
    // 强制推进纪元并回收
    DefaultEBR::force_reclaim();
}

TEST_F(SMRTest, EpochProgression) {
    auto initial_epoch = DefaultEBR::current_global_epoch();
    
    // 多次进入和退出纪元守护应该推进全局纪元
    for (int i = 0; i < 10; ++i) {
        DefaultEBR::EpochGuard guard;
        // 在守护范围内做一些工作
        std::this_thread::sleep_for(std::chrono::microseconds(100));
    }
    
    // 强制推进纪元
    DefaultEBR::force_reclaim();
    
    auto final_epoch = DefaultEBR::current_global_epoch();
    EXPECT_GE(final_epoch, initial_epoch);
}

/**
 * SMR 保护队列的并发测试
 */
TEST_F(SMRTest, HazardProtectedQueueConcurrent) {
    HazardProtectedQueue<int> queue;
    
    const int operations_per_thread = 500;
    std::atomic<int> total_enqueued{0};
    std::atomic<int> total_dequeued{0};
    
    std::vector<std::thread> threads;
    
    // 生产者线程
    for (int i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&, i]() {
            int enqueued = 0;
            for (int j = 0; j < operations_per_thread; ++j) {
                int value = i * operations_per_thread + j;
                queue.enqueue(value);
                ++enqueued;
            }
            total_enqueued.fetch_add(enqueued);
        });
    }
    
    // 消费者线程
    std::vector<std::vector<int>> consumed_values(THREAD_COUNT / 2);
    for (int i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&, i]() {
            int dequeued = 0;
            int value;
            
            while (dequeued < operations_per_thread) {
                if (queue.dequeue(value)) {
                    consumed_values[i].push_back(value);
                    ++dequeued;
                } else {
                    std::this_thread::yield();
                }
            }
            total_dequeued.fetch_add(dequeued);
        });
    }
    
    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }
    
    // 验证结果
    int expected_total = (THREAD_COUNT / 2) * operations_per_thread;
    EXPECT_EQ(total_enqueued.load(), expected_total);
    EXPECT_EQ(total_dequeued.load(), expected_total);
    
    // 验证没有重复消费
    std::set<int> all_consumed;
    for (const auto& thread_values : consumed_values) {
        for (int value : thread_values) {
            EXPECT_TRUE(all_consumed.find(value) == all_consumed.end()) 
                << "Value " << value << " consumed multiple times";
            all_consumed.insert(value);
        }
    }
    
    EXPECT_EQ(all_consumed.size(), expected_total);
    
    // 清理
    DefaultHazardPointers::thread_exit();
}

TEST_F(SMRTest, EpochProtectedQueueConcurrent) {
    EpochProtectedQueue<int> queue;
    
    const int operations_per_thread = 500;
    std::atomic<int> total_enqueued{0};
    std::atomic<int> total_dequeued{0};
    
    std::vector<std::thread> threads;
    
    // 生产者线程
    for (int i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&, i]() {
            int enqueued = 0;
            for (int j = 0; j < operations_per_thread; ++j) {
                int value = i * operations_per_thread + j;
                queue.enqueue(value);
                ++enqueued;
            }
            total_enqueued.fetch_add(enqueued);
        });
    }
    
    // 消费者线程
    std::vector<std::vector<int>> consumed_values(THREAD_COUNT / 2);
    for (int i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&, i]() {
            int dequeued = 0;
            int value;
            
            while (dequeued < operations_per_thread) {
                if (queue.dequeue(value)) {
                    consumed_values[i].push_back(value);
                    ++dequeued;
                } else {
                    std::this_thread::yield();
                }
            }
            total_dequeued.fetch_add(dequeued);
        });
    }
    
    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }
    
    // 验证结果
    int expected_total = (THREAD_COUNT / 2) * operations_per_thread;
    EXPECT_EQ(total_enqueued.load(), expected_total);
    EXPECT_EQ(total_dequeued.load(), expected_total);
    
    // 验证没有重复消费
    std::set<int> all_consumed;
    for (const auto& thread_values : consumed_values) {
        for (int value : thread_values) {
            EXPECT_TRUE(all_consumed.find(value) == all_consumed.end()) 
                << "Value " << value << " consumed multiple times";
            all_consumed.insert(value);
        }
    }
    
    EXPECT_EQ(all_consumed.size(), expected_total);
    
    // 清理
    DefaultEBR::thread_exit();
}

/**
 * 内存泄漏检测测试
 */

// 独立的测试对象类（放在函数外部）
struct TestObjectForReclaim {
    static std::atomic<int> instance_count;
    int value;

    TestObjectForReclaim(int v = 0) : value(v) {
        instance_count.fetch_add(1);
    }

    ~TestObjectForReclaim() {
        instance_count.fetch_sub(1);
    }
};

// 定义静态成员
std::atomic<int> TestObjectForReclaim::instance_count{0};

TEST_F(SMRTest, MemoryReclamationTest) {
    // 测试 Hazard Pointers 的内存回收
    {
        int initial_count = TestObjectForReclaim::instance_count.load();

        // 创建和退休一些对象
        for (int i = 0; i < 100; ++i) {
            auto* obj = new TestObjectForReclaim(i);
            DefaultHazardPointers::retire(obj);
        }

        // 强制回收
        DefaultHazardPointers::force_gc();

        int final_count = TestObjectForReclaim::instance_count.load();
        EXPECT_EQ(final_count, initial_count) << "Memory leak detected in Hazard Pointers";
    }

    // 测试 Epoch-based Reclamation 的内存回收
    {
        int initial_count = TestObjectForReclaim::instance_count.load();

        {
            DefaultEBR::EpochGuard guard;

            for (int i = 0; i < 100; ++i) {
                auto* obj = new TestObjectForReclaim(i);
                DefaultEBR::defer_reclamation(obj);
            }
        }

        // 强制回收
        DefaultEBR::force_reclaim();

        int final_count = TestObjectForReclaim::instance_count.load();
        EXPECT_EQ(final_count, initial_count) << "Memory leak detected in EBR";
    }
}

/**
 * 压力测试：模拟高竞争环境
 */
TEST_F(SMRTest, StressTest) {
    const int thread_count = 8;
    const int operations_per_thread = 1000;
    
    // Hazard Pointers 压力测试
    {
        std::vector<std::thread> threads;
        std::atomic<int> operations_completed{0};
        
        for (int i = 0; i < thread_count; ++i) {
            threads.emplace_back([&, i]() {
                std::random_device rd;
                std::mt19937 gen(rd());
                std::uniform_int_distribution<> dis(1, 100);
                
                for (int j = 0; j < operations_per_thread; ++j) {
                    // 随机分配和退休对象
                    auto* obj = new int(dis(gen));
                    
                    // 有时候保护对象
                    if (j % 10 == 0) {
                        DefaultHazardPointers::HazardGuard<int> guard;
                        guard.set_protection(obj);
                        
                        // 做一些工作
                        std::this_thread::sleep_for(std::chrono::microseconds(1));
                        
                        guard.clear_protection();
                    }
                    
                    DefaultHazardPointers::retire(obj);
                    
                    // 定期强制 GC
                    if (j % 50 == 0) {
                        DefaultHazardPointers::force_gc();
                    }
                }
                
                operations_completed.fetch_add(operations_per_thread);
            });
        }
        
        for (auto& t : threads) {
            t.join();
        }
        
        EXPECT_EQ(operations_completed.load(), thread_count * operations_per_thread);
        DefaultHazardPointers::force_gc();
    }
    
    // EBR 压力测试
    {
        std::vector<std::thread> threads;
        std::atomic<int> operations_completed{0};
        
        for (int i = 0; i < thread_count; ++i) {
            threads.emplace_back([&, i]() {
                std::random_device rd;
                std::mt19937 gen(rd());
                std::uniform_int_distribution<> dis(1, 100);
                
                for (int j = 0; j < operations_per_thread; ++j) {
                    DefaultEBR::EpochGuard guard;
                    
                    // 随机分配和退休对象
                    auto* obj = new int(dis(gen));
                    DefaultEBR::defer_reclamation(obj);
                    
                    // 定期强制回收
                    if (j % 50 == 0) {
                        DefaultEBR::force_reclaim();
                    }
                }
                
                operations_completed.fetch_add(operations_per_thread);
            });
        }
        
        for (auto& t : threads) {
            t.join();
        }
        
        EXPECT_EQ(operations_completed.load(), thread_count * operations_per_thread);
        DefaultEBR::force_reclaim();
    }
}

/**
 * 性能对比测试
 */
TEST_F(SMRTest, PerformanceComparison) {
    const int operations = 10000;
    
    std::cout << "\n=== SMR 性能对比测试 ===" << std::endl;
    
    // Hazard Pointers 性能
    {
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < operations; ++i) {
            DefaultHazardPointers::HazardGuard<int> guard;
            auto* obj = new int(i);
            guard.set_protection(obj);
            DefaultHazardPointers::retire(obj);
            guard.clear_protection();
        }
        
        DefaultHazardPointers::force_gc();
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Hazard Pointers: " << duration.count() << " μs" << std::endl;
    }
    
    // Epoch-based Reclamation 性能
    {
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < operations; ++i) {
            DefaultEBR::EpochGuard guard;
            auto* obj = new int(i);
            DefaultEBR::defer_reclamation(obj);
        }
        
        DefaultEBR::force_reclaim();
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Epoch-based Reclamation: " << duration.count() << " μs" << std::endl;
    }
}
