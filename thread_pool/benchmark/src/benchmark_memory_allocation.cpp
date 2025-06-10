#include "benchmark_framework.hpp"
#include <thread>
#include <vector>
#include <future>

// A task that performs many small memory allocations and deallocations.
static void MemoryIntensiveTask(int iterations, int alloc_size) {
    for (int i = 0; i < iterations; ++i) {
        // Use volatile to prevent the compiler from optimizing away the allocations.
        volatile char* p = new char[alloc_size];
        delete[] p;
    }
}

// Benchmark fixture for memory allocation tests.
class MemoryBenchmark : public benchmark::Fixture {
public:
    void SetUp(const ::benchmark::State& state) override {
        pool_adapter = std::make_unique<tp_bench::OriginalThreadPoolAdapter>();
        pool_adapter->initialize(state.range(0));
    }

    void TearDown(const ::benchmark::State& /*state*/) override {
        pool_adapter->shutdown();
        pool_adapter.reset();
    }

protected:
    std::unique_ptr<tp_bench::ThreadPoolAdapter> pool_adapter;
};

// Define and register the benchmark.
// This benchmark measures the performance of memory allocations with the default allocator.
BENCHMARK_DEFINE_F(MemoryBenchmark, AllocatorTest)(benchmark::State& state) {
    int thread_count = state.range(0);
    int total_tasks = state.range(1);
    int alloc_size = state.range(2);
    int alloc_iterations = 100; // Number of allocations per task

    for (auto _ : state) {
        std::vector<std::future<void>> futures;
        futures.reserve(total_tasks);
        for (int i = 0; i < total_tasks; ++i) {
            futures.emplace_back(pool_adapter->submit_task([=] {
                MemoryIntensiveTask(alloc_iterations, alloc_size);
            }));
        }

        for (auto& f : futures) {
            f.get();
        }
    }

    std::string label = "default_allocator";
#ifdef USE_TCMALLOC
    label = "tcmalloc";
#endif

    state.SetLabel(label + "/" + std::to_string(thread_count) + " threads");
    state.SetItemsProcessed(state.iterations() * total_tasks);
    state.SetBytesProcessed(state.iterations() * total_tasks * alloc_iterations * alloc_size);
}

BENCHMARK_REGISTER_F(MemoryBenchmark, AllocatorTest)
    ->ArgsProduct({
        benchmark::CreateRange(1, std::thread::hardware_concurrency() * 2, 2),  // Thread count
        {1000}, // Total tasks
        {128}   // Allocation size (bytes)
    })
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime(); 