#pragma once

#include <atomic>
#include <vector>
#include <array>
#include <thread>
#include <unordered_set>
#include <algorithm>
#include <functional>
#include <cassert>

namespace stage4 {

/**
 * Hazard Pointers (危险指针) 实现
 * 
 * Hazard Pointers 是 Maged M. Michael 提出的一种安全内存回收技术。
 * 
 * 核心思想：
 * 1. 每个线程维护一个"危险指针"列表，声明它当前正在访问的内存地址
 * 2. 要删除的对象会被放入一个"退休列表"
 * 3. 只有当一个对象不被任何线程的危险指针保护时，才能被真正删除
 * 
 * 优点：
 * - 确保内存安全，避免访问已释放的内存
 * - 适用于各种无锁数据结构
 * - 实现相对简单
 * 
 * 缺点：
 * - 需要扫描所有线程的危险指针，开销较大
 * - 内存回收可能延迟
 */

template<size_t MAX_HAZARDS_PER_THREAD = 8>
class HazardPointers {
public:
    /**
     * 危险指针记录
     * 每个线程都有一个这样的记录
     */
    struct HazardRecord {
        std::thread::id thread_id;
        std::array<std::atomic<void*>, MAX_HAZARDS_PER_THREAD> hazards;
        std::atomic<bool> active;
        
        HazardRecord() : thread_id(), active(false) {
            for (auto& hazard : hazards) {
                hazard.store(nullptr, std::memory_order_relaxed);
            }
        }
    };
    
    /**
     * 退休节点，等待回收的对象
     */
    struct RetiredNode {
        void* ptr;
        std::function<void(void*)> deleter;
        
        RetiredNode(void* p, std::function<void(void*)> del) 
            : ptr(p), deleter(std::move(del)) {}
    };

private:
    static constexpr size_t MAX_THREADS = 128;
    static constexpr size_t RETIRED_THRESHOLD = 64;  // 退休列表阈值
    
    // 全局危险指针记录数组
    static std::array<HazardRecord, MAX_THREADS> hazard_records_;
    static std::atomic<size_t> record_count_;
    
    // 线程本地存储
    thread_local static HazardRecord* local_hazard_record_;
    thread_local static std::vector<RetiredNode> retired_list_;
    
    /**
     * 获取当前线程的危险指针记录
     */
    static HazardRecord* get_hazard_record() {
        if (local_hazard_record_ == nullptr) {
            // 寻找一个空闲的记录或创建新的
            for (auto& record : hazard_records_) {
                std::thread::id empty_id{};
                if (record.thread_id == empty_id && 
                    !record.active.load(std::memory_order_acquire)) {
                    
                    // 尝试占用这个记录
                    bool expected = false;
                    if (record.active.compare_exchange_strong(expected, true,
                                                            std::memory_order_acq_rel)) {
                        record.thread_id = std::this_thread::get_id();
                        local_hazard_record_ = &record;
                        record_count_.fetch_add(1, std::memory_order_relaxed);
                        break;
                    }
                }
            }
            assert(local_hazard_record_ != nullptr && "Too many threads using hazard pointers");
        }
        return local_hazard_record_;
    }
    
    /**
     * 收集所有活跃的危险指针
     */
    static std::unordered_set<void*> collect_hazards() {
        std::unordered_set<void*> hazards;
        
        for (const auto& record : hazard_records_) {
            if (record.active.load(std::memory_order_acquire)) {
                for (const auto& hazard : record.hazards) {
                    void* ptr = hazard.load(std::memory_order_acquire);
                    if (ptr != nullptr) {
                        hazards.insert(ptr);
                    }
                }
            }
        }
        
        return hazards;
    }
    
    /**
     * 尝试回收退休列表中的对象
     */
    static void reclaim_retired_objects() {
        if (retired_list_.size() < RETIRED_THRESHOLD) {
            return;
        }
        
        // 收集所有危险指针
        auto hazards = collect_hazards();
        
        // 扫描退休列表，回收不被保护的对象
        auto it = retired_list_.begin();
        while (it != retired_list_.end()) {
            if (hazards.find(it->ptr) == hazards.end()) {
                // 这个对象没有被任何危险指针保护，可以安全删除
                it->deleter(it->ptr);
                it = retired_list_.erase(it);
            } else {
                ++it;
            }
        }
    }

public:
    /**
     * 危险指针保护器
     * RAII 风格的危险指针管理
     */
    template<typename T>
    class HazardGuard {
    private:
        std::atomic<void*>* hazard_slot_;
        
    public:
        explicit HazardGuard(size_t slot_index = 0) {
            assert(slot_index < MAX_HAZARDS_PER_THREAD);
            HazardRecord* record = get_hazard_record();
            hazard_slot_ = &record->hazards[slot_index];
        }
        
        ~HazardGuard() {
            if (hazard_slot_) {
                hazard_slot_->store(nullptr, std::memory_order_release);
            }
        }
        
        // 禁止拷贝
        HazardGuard(const HazardGuard&) = delete;
        HazardGuard& operator=(const HazardGuard&) = delete;
        
        // 允许移动
        HazardGuard(HazardGuard&& other) noexcept 
            : hazard_slot_(other.hazard_slot_) {
            other.hazard_slot_ = nullptr;
        }
        
        HazardGuard& operator=(HazardGuard&& other) noexcept {
            if (this != &other) {
                if (hazard_slot_) {
                    hazard_slot_->store(nullptr, std::memory_order_release);
                }
                hazard_slot_ = other.hazard_slot_;
                other.hazard_slot_ = nullptr;
            }
            return *this;
        }
        
        /**
         * 保护一个指针
         * @param ptr 要保护的指针
         * @return 保护的指针值（可能已经变化）
         */
        T* protect(std::atomic<T*>& ptr) {
            T* current;
            do {
                current = ptr.load(std::memory_order_acquire);
                hazard_slot_->store(current, std::memory_order_release);
                // 再次检查指针是否仍然相同，避免 ABA 问题
            } while (current != ptr.load(std::memory_order_acquire));
            
            return current;
        }
        
        /**
         * 手动设置保护的指针
         */
        void set_protection(T* ptr) {
            hazard_slot_->store(ptr, std::memory_order_release);
        }
        
        /**
         * 清除保护
         */
        void clear_protection() {
            hazard_slot_->store(nullptr, std::memory_order_release);
        }
    };
    
    /**
     * 退休一个对象，等待安全回收
     * @param ptr 要退休的指针
     * @param deleter 删除函数
     */
    template<typename T>
    static void retire(T* ptr, std::function<void(T*)> deleter = nullptr) {
        if (ptr == nullptr) return;
        
        // 默认删除器
        if (!deleter) {
            deleter = [](T* p) { delete p; };
        }
        
        // 包装删除器
        auto wrapped_deleter = [deleter](void* p) {
            deleter(static_cast<T*>(p));
        };
        
        retired_list_.emplace_back(ptr, wrapped_deleter);
        
        // 尝试回收
        reclaim_retired_objects();
    }
    
    /**
     * 强制执行垃圾回收
     */
    static void force_gc() {
        reclaim_retired_objects();
    }
    
    /**
     * 线程退出时清理资源
     */
    static void thread_exit() {
        if (local_hazard_record_) {
            // 清除所有危险指针
            for (auto& hazard : local_hazard_record_->hazards) {
                hazard.store(nullptr, std::memory_order_release);
            }
            
            // 标记为非活跃
            local_hazard_record_->active.store(false, std::memory_order_release);
            local_hazard_record_->thread_id = std::thread::id{};
            
            record_count_.fetch_sub(1, std::memory_order_relaxed);
            local_hazard_record_ = nullptr;
        }
        
        // 强制回收所有退休对象
        auto hazards = collect_hazards();
        for (auto& retired : retired_list_) {
            if (hazards.find(retired.ptr) == hazards.end()) {
                retired.deleter(retired.ptr);
            }
        }
        retired_list_.clear();
    }
    
    /**
     * 获取统计信息
     */
    struct Statistics {
        size_t active_threads;
        size_t total_hazards;
        size_t retired_objects;
    };
    
    static Statistics get_statistics() {
        Statistics stats{};
        stats.active_threads = record_count_.load(std::memory_order_acquire);
        
        for (const auto& record : hazard_records_) {
            if (record.active.load(std::memory_order_acquire)) {
                for (const auto& hazard : record.hazards) {
                    if (hazard.load(std::memory_order_acquire) != nullptr) {
                        ++stats.total_hazards;
                    }
                }
            }
        }
        
        stats.retired_objects = retired_list_.size();
        return stats;
    }
};

// 静态成员定义
template<size_t MAX_HAZARDS_PER_THREAD>
std::array<typename HazardPointers<MAX_HAZARDS_PER_THREAD>::HazardRecord, 
           HazardPointers<MAX_HAZARDS_PER_THREAD>::MAX_THREADS> 
    HazardPointers<MAX_HAZARDS_PER_THREAD>::hazard_records_;

template<size_t MAX_HAZARDS_PER_THREAD>
std::atomic<size_t> HazardPointers<MAX_HAZARDS_PER_THREAD>::record_count_{0};

template<size_t MAX_HAZARDS_PER_THREAD>
thread_local typename HazardPointers<MAX_HAZARDS_PER_THREAD>::HazardRecord* 
    HazardPointers<MAX_HAZARDS_PER_THREAD>::local_hazard_record_{nullptr};

template<size_t MAX_HAZARDS_PER_THREAD>
thread_local std::vector<typename HazardPointers<MAX_HAZARDS_PER_THREAD>::RetiredNode> 
    HazardPointers<MAX_HAZARDS_PER_THREAD>::retired_list_;

// 便利别名
using DefaultHazardPointers = HazardPointers<8>;

/**
 * 使用 Hazard Pointers 的 Michael-Scott 队列
 * 
 * 这个版本展示了如何将 Hazard Pointers 集成到无锁数据结构中
 */
template<typename T>
class HazardProtectedQueue {
private:
    struct Node {
        std::atomic<T*> data;
        std::atomic<Node*> next;
        
        Node() : data(nullptr), next(nullptr) {}
        explicit Node(T* item) : data(item), next(nullptr) {}
    };
    
    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
    
public:
    HazardProtectedQueue() {
        Node* dummy = new Node();
        head_.store(dummy, std::memory_order_relaxed);
        tail_.store(dummy, std::memory_order_relaxed);
    }
    
    ~HazardProtectedQueue() {
        Node* current = head_.load(std::memory_order_relaxed);
        while (current != nullptr) {
            Node* next = current->next.load(std::memory_order_relaxed);
            T* data = current->data.load(std::memory_order_relaxed);
            if (data != nullptr) {
                delete data;
            }
            delete current;
            current = next;
        }
    }
    
    void enqueue(const T& item) {
        T* data = new T(item);
        Node* new_node = new Node(data);
        
        DefaultHazardPointers::HazardGuard<Node> tail_guard(0);
        
        while (true) {
            Node* tail = tail_guard.protect(tail_);
            Node* next = tail->next.load(std::memory_order_acquire);
            
            if (tail == tail_.load(std::memory_order_acquire)) {
                if (next == nullptr) {
                    if (tail->next.compare_exchange_weak(next, new_node,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed)) {
                        tail_.compare_exchange_weak(tail, new_node,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed);
                        break;
                    }
                } else {
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                }
            }
        }
    }
    
    bool dequeue(T& item) {
        DefaultHazardPointers::HazardGuard<Node> head_guard(0);
        DefaultHazardPointers::HazardGuard<Node> next_guard(1);
        
        while (true) {
            Node* head = head_guard.protect(head_);
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = next_guard.protect(head->next);
            
            if (head == head_.load(std::memory_order_acquire)) {
                if (head == tail) {
                    if (next == nullptr) {
                        return false;  // 空队列
                    }
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                } else {
                    if (next == nullptr) {
                        continue;
                    }
                    
                    T* data = next->data.load(std::memory_order_acquire);
                    if (data == nullptr) {
                        continue;
                    }
                    
                    if (head_.compare_exchange_weak(head, next,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed)) {
                        item = *data;
                        delete data;
                        
                        // 使用 Hazard Pointers 安全回收旧节点
                        DefaultHazardPointers::retire(head);
                        return true;
                    }
                }
            }
        }
    }
    
    bool empty() const {
        DefaultHazardPointers::HazardGuard<Node> head_guard(0);
        Node* head = head_guard.protect(head_);
        Node* tail = tail_.load(std::memory_order_acquire);
        return (head == tail) && (head->next.load(std::memory_order_acquire) == nullptr);
    }
};

} // namespace stage4
