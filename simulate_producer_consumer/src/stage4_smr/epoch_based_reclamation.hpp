#pragma once

#include <atomic>
#include <vector>
#include <array>
#include <thread>
#include <functional>
#include <cassert>
#include <algorithm>

namespace stage4 {

/**
 * Epoch-based Reclamation (EBR) 实现
 * 
 * EBR 是另一种安全内存回收技术，相比 Hazard Pointers 有以下特点：
 * 
 * 核心思想：
 * 1. 系统维护一个全局的"纪元"(epoch) 计数器
 * 2. 每个线程都处于某个纪元中
 * 3. 删除的对象被标记为当前纪元，并放入待回收列表
 * 4. 只有当所有线程都离开某个纪元时，该纪元的对象才能被安全回收
 * 
 * 优点：
 * - 比 Hazard Pointers 更高效，因为不需要扫描危险指针
 * - 批量回收，减少碎片化
 * - 实现相对简单
 * 
 * 缺点：
 * - 如果某个线程长时间停留在旧纪元，会阻止内存回收
 * - 需要定期推进纪元
 */

template<size_t MAX_THREADS = 128>
class EpochBasedReclamation {
public:
    using epoch_t = uint64_t;
    
    /**
     * 线程纪元记录
     */
    struct ThreadRecord {
        std::atomic<epoch_t> local_epoch;
        std::atomic<bool> active;
        std::thread::id thread_id;
        
        ThreadRecord() : local_epoch(0), active(false), thread_id() {}
    };
    
    /**
     * 待回收对象
     */
    struct DeferredNode {
        void* ptr;
        std::function<void(void*)> deleter;
        epoch_t birth_epoch;
        
        DeferredNode(void* p, std::function<void(void*)> del, epoch_t epoch)
            : ptr(p), deleter(std::move(del)), birth_epoch(epoch) {}
    };

private:
    // 全局纪元
    static std::atomic<epoch_t> global_epoch_;
    
    // 线程记录数组
    static std::array<ThreadRecord, MAX_THREADS> thread_records_;
    static std::atomic<size_t> active_threads_;
    
    // 线程本地存储
    thread_local static ThreadRecord* local_record_;
    thread_local static std::vector<DeferredNode> deferred_list_;
    thread_local static epoch_t last_epoch_check_;
    
    static constexpr size_t DEFERRED_THRESHOLD = 64;
    static constexpr epoch_t EPOCH_ADVANCE_FREQUENCY = 100;
    
    /**
     * 获取当前线程的记录
     */
    static ThreadRecord* get_thread_record() {
        if (local_record_ == nullptr) {
            // 寻找空闲的记录
            for (auto& record : thread_records_) {
                bool expected = false;
                if (record.active.compare_exchange_strong(expected, true,
                                                        std::memory_order_acq_rel)) {
                    record.thread_id = std::this_thread::get_id();
                    record.local_epoch.store(global_epoch_.load(std::memory_order_acquire),
                                           std::memory_order_relaxed);
                    local_record_ = &record;
                    active_threads_.fetch_add(1, std::memory_order_relaxed);
                    break;
                }
            }
            assert(local_record_ != nullptr && "Too many threads using EBR");
        }
        return local_record_;
    }
    
    /**
     * 尝试推进全局纪元
     */
    static bool try_advance_global_epoch() {
        epoch_t current_global = global_epoch_.load(std::memory_order_acquire);
        epoch_t min_local_epoch = current_global;
        
        // 找到所有活跃线程的最小纪元
        for (const auto& record : thread_records_) {
            if (record.active.load(std::memory_order_acquire)) {
                epoch_t local_epoch = record.local_epoch.load(std::memory_order_acquire);
                min_local_epoch = std::min(min_local_epoch, local_epoch);
            }
        }
        
        // 如果所有线程都已经进入当前纪元，可以推进到下一个纪元
        if (min_local_epoch == current_global) {
            return global_epoch_.compare_exchange_strong(current_global, current_global + 1,
                                                       std::memory_order_acq_rel);
        }
        
        return false;
    }
    
    /**
     * 回收旧纪元的对象
     */
    static void reclaim_deferred_objects() {
        if (deferred_list_.empty()) {
            return;
        }
        
        // 获取当前可以安全回收的纪元阈值
        epoch_t safe_epoch = global_epoch_.load(std::memory_order_acquire);
        if (safe_epoch <= 2) {
            return;  // 需要至少3个纪元的缓冲
        }
        safe_epoch -= 2;
        
        // 回收足够旧的对象
        auto it = deferred_list_.begin();
        while (it != deferred_list_.end()) {
            if (it->birth_epoch <= safe_epoch) {
                it->deleter(it->ptr);
                it = deferred_list_.erase(it);
            } else {
                ++it;
            }
        }
    }

public:
    /**
     * 纪元守护者
     * RAII 风格的纪元管理，确保线程在操作期间保持在当前纪元
     */
    class EpochGuard {
    private:
        ThreadRecord* record_;
        epoch_t entered_epoch_;
        
    public:
        EpochGuard() : record_(get_thread_record()) {
            // 进入当前纪元
            entered_epoch_ = global_epoch_.load(std::memory_order_acquire);
            record_->local_epoch.store(entered_epoch_, std::memory_order_release);
        }
        
        ~EpochGuard() {
            // 可以选择在这里推进纪元或延迟到下次操作
            if (++last_epoch_check_ % EPOCH_ADVANCE_FREQUENCY == 0) {
                try_advance_global_epoch();
                reclaim_deferred_objects();
            }
        }
        
        // 禁止拷贝和移动
        EpochGuard(const EpochGuard&) = delete;
        EpochGuard& operator=(const EpochGuard&) = delete;
        EpochGuard(EpochGuard&&) = delete;
        EpochGuard& operator=(EpochGuard&&) = delete;
        
        /**
         * 获取当前纪元
         */
        epoch_t current_epoch() const {
            return entered_epoch_;
        }
    };
    
    /**
     * 延迟回收一个对象
     * @param ptr 要回收的指针
     * @param deleter 删除函数
     */
    template<typename T>
    static void defer_reclamation(T* ptr, std::function<void(T*)> deleter = nullptr) {
        if (ptr == nullptr) return;
        
        // 默认删除器
        if (!deleter) {
            deleter = [](T* p) { delete p; };
        }
        
        // 包装删除器
        auto wrapped_deleter = [deleter](void* p) {
            deleter(static_cast<T*>(p));
        };
        
        epoch_t current_epoch = global_epoch_.load(std::memory_order_acquire);
        deferred_list_.emplace_back(ptr, wrapped_deleter, current_epoch);
        
        // 如果延迟列表太长，尝试回收
        if (deferred_list_.size() >= DEFERRED_THRESHOLD) {
            reclaim_deferred_objects();
        }
    }
    
    /**
     * 强制推进纪元并回收对象
     */
    static void force_reclaim() {
        try_advance_global_epoch();
        reclaim_deferred_objects();
    }
    
    /**
     * 线程退出时清理
     */
    static void thread_exit() {
        if (local_record_) {
            // 回收所有延迟对象
            for (auto& deferred : deferred_list_) {
                deferred.deleter(deferred.ptr);
            }
            deferred_list_.clear();
            
            // 释放线程记录
            local_record_->active.store(false, std::memory_order_release);
            local_record_->thread_id = std::thread::id{};
            local_record_->local_epoch.store(0, std::memory_order_relaxed);
            
            active_threads_.fetch_sub(1, std::memory_order_relaxed);
            local_record_ = nullptr;
        }
    }
    
    /**
     * 获取统计信息
     */
    struct Statistics {
        epoch_t global_epoch;
        size_t active_threads;
        size_t deferred_objects;
        epoch_t min_thread_epoch;
        epoch_t max_thread_epoch;
    };
    
    static Statistics get_statistics() {
        Statistics stats{};
        stats.global_epoch = global_epoch_.load(std::memory_order_acquire);
        stats.active_threads = active_threads_.load(std::memory_order_acquire);
        stats.deferred_objects = deferred_list_.size();
        stats.min_thread_epoch = stats.global_epoch;
        stats.max_thread_epoch = 0;
        
        for (const auto& record : thread_records_) {
            if (record.active.load(std::memory_order_acquire)) {
                epoch_t local_epoch = record.local_epoch.load(std::memory_order_acquire);
                stats.min_thread_epoch = std::min(stats.min_thread_epoch, local_epoch);
                stats.max_thread_epoch = std::max(stats.max_thread_epoch, local_epoch);
            }
        }
        
        return stats;
    }
    
    /**
     * 获取当前全局纪元
     */
    static epoch_t current_global_epoch() {
        return global_epoch_.load(std::memory_order_acquire);
    }
};

// 静态成员定义
template<size_t MAX_THREADS>
std::atomic<typename EpochBasedReclamation<MAX_THREADS>::epoch_t> 
    EpochBasedReclamation<MAX_THREADS>::global_epoch_{0};

template<size_t MAX_THREADS>
std::array<typename EpochBasedReclamation<MAX_THREADS>::ThreadRecord, MAX_THREADS>
    EpochBasedReclamation<MAX_THREADS>::thread_records_;

template<size_t MAX_THREADS>
std::atomic<size_t> EpochBasedReclamation<MAX_THREADS>::active_threads_{0};

template<size_t MAX_THREADS>
thread_local typename EpochBasedReclamation<MAX_THREADS>::ThreadRecord*
    EpochBasedReclamation<MAX_THREADS>::local_record_{nullptr};

template<size_t MAX_THREADS>
thread_local std::vector<typename EpochBasedReclamation<MAX_THREADS>::DeferredNode>
    EpochBasedReclamation<MAX_THREADS>::deferred_list_;

template<size_t MAX_THREADS>
thread_local typename EpochBasedReclamation<MAX_THREADS>::epoch_t
    EpochBasedReclamation<MAX_THREADS>::last_epoch_check_{0};

// 便利别名
using DefaultEBR = EpochBasedReclamation<128>;

/**
 * 使用 Epoch-based Reclamation 的 Michael-Scott 队列
 */
template<typename T>
class EpochProtectedQueue {
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
    EpochProtectedQueue() {
        Node* dummy = new Node();
        head_.store(dummy, std::memory_order_relaxed);
        tail_.store(dummy, std::memory_order_relaxed);
    }
    
    ~EpochProtectedQueue() {
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
        DefaultEBR::EpochGuard guard;  // 进入当前纪元
        
        T* data = new T(item);
        Node* new_node = new Node(data);
        
        while (true) {
            Node* tail = tail_.load(std::memory_order_acquire);
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
        DefaultEBR::EpochGuard guard;  // 进入当前纪元
        
        while (true) {
            Node* head = head_.load(std::memory_order_acquire);
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = head->next.load(std::memory_order_acquire);
            
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
                        
                        // 使用 EBR 延迟回收旧节点
                        DefaultEBR::defer_reclamation(head);
                        return true;
                    }
                }
            }
        }
    }
    
    bool empty() const {
        DefaultEBR::EpochGuard guard;
        
        Node* head = head_.load(std::memory_order_acquire);
        Node* tail = tail_.load(std::memory_order_acquire);
        return (head == tail) && (head->next.load(std::memory_order_acquire) == nullptr);
    }
};

/**
 * SMR 技术对比和选择指南
 * 
 * Hazard Pointers vs Epoch-based Reclamation:
 * 
 * Hazard Pointers:
 * + 适合读多写少的场景
 * + 内存回收及时
 * + 对线程行为无要求
 * - 扫描危险指针有开销
 * - 每个线程需要维护危险指针列表
 * 
 * Epoch-based Reclamation:
 * + 性能更高，特别是在高并发场景
 * + 批量回收减少碎片
 * + 实现相对简单
 * - 可能因某个线程阻塞而延迟内存回收
 * - 需要定期推进纪元
 * 
 * 选择建议：
 * 1. 高性能场景且线程行为可控 -> EBR
 * 2. 线程可能长时间阻塞 -> Hazard Pointers
 * 3. 简单应用场景 -> 直接使用成熟库如 boost::lockfree
 */

} // namespace stage4
