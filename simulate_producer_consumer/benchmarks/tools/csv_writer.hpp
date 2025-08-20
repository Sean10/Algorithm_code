#pragma once

#include <cstdio>
#include <cstring>
#include <unistd.h>

namespace bench_tools {

inline void append_latency_csv(const char* path,
                               const char* queue_label,
                               int consumer_count,
                               int test_count,
                               double** all_latencies) {
    if (path == NULL || path[0] == '\0') return;
    bool need_header = access(path, F_OK) != 0;
    FILE* fp = std::fopen(path, "a");
    if (!fp) {
        std::perror("打开延迟CSV失败");
        return;
    }
    if (need_header) {
        std::fprintf(fp, "queue_type,consumer_id,sample_idx,latency_us\n");
    }
    for (int i = 0; i < consumer_count; ++i) {
        for (int j = 0; j < test_count; ++j) {
            double latency = all_latencies[i][j];
            if (latency >= 0) {
                std::fprintf(fp, "%s,%d,%d,%.6f\n", queue_label, i, j, latency);
            }
        }
    }
    std::fclose(fp);
}

inline void append_summary_csv(const char* path,
                               const char* queue_label,
                               int queue_size,
                               int test_count,
                               int consumer_count,
                               int timeout_seconds,
                               int total_samples,
                               double avg_latency,
                               double min_latency,
                               double max_latency) {
    if (path == NULL || path[0] == '\0') return;
    bool need_header = access(path, F_OK) != 0;
    FILE* fp = std::fopen(path, "a");
    if (!fp) {
        std::perror("打开汇总CSV失败");
        return;
    }
    if (need_header) {
        std::fprintf(fp, "queue_type,queue_size,test_count,consumers,timeout_s,total_samples,avg_latency_us,min_latency_us,max_latency_us,throughput_est\n");
    }
    double throughput = (avg_latency > 0) ? (1000000.0 / avg_latency * consumer_count) : 0.0;
    std::fprintf(fp,
                 "%s,%d,%d,%d,%d,%d,%.6f,%.6f,%.6f,%.6f\n",
                 queue_label, queue_size, test_count, consumer_count, timeout_seconds,
                 total_samples, avg_latency, min_latency, max_latency, throughput);
    std::fclose(fp);
}

} // namespace bench_tools


