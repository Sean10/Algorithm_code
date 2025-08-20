
#include <atomic>  

using namespace std;
  
template <typename T>  
class LockFreeArrayQueue {  
private:  
    T* buffer;  
    std::atomic<size_t> head, tail;  
    const size_t capacity;  
  
public:  
    LockFreeArrayQueue(size_t capacity)  
        : buffer(new T[capacity]), head(0), tail(0), capacity(capacity) {}  
  
    ~LockFreeArrayQueue() {  
        delete[] buffer;  
    }  
  
    bool enqueue(T item) {  
        size_t newTail = (tail.load() + 1) % capacity;  
        if (newTail == head.load()) {  
            // 队列满  
            return false;  
        }  
        while (true) {  
            size_t currTail = tail.load();  
            if (currTail == newTail) {  
                // 队列满，或tail被其他线程更新  
                continue;  
            }  
            if (tail.compare_exchange_weak(currTail, newTail)) {  
                buffer[currTail] = item;  
                return true;  
            }  
            // CAS失败，重试  
        }  
    }  
  
    bool dequeue(T& item) {  
        if (head.load() == tail.load()) {  
            // 队列空  
            return false;  
        }  
        while (true) {  
            size_t currHead = head.load();  
            size_t newHead = (currHead + 1) % capacity;  
            if (currHead == tail.load()) {  
                // 队列空，或head被其他线程更新  
                continue;  
            }  
            if (head.compare_exchange_weak(currHead, newHead)) {  
                item = buffer[currHead];  
                return true;  
            }  
            // CAS失败，重试  
        }  
    }  
};
