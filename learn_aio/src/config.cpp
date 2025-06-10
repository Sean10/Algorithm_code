#include "config.h"
#include <iostream>
#include <getopt.h>
#include <cstring>
#include <algorithm>
#include <cctype>

namespace aio_bench {

bool Config::parse_args(int argc, char* argv[]) {
    static struct option long_options[] = {
        {"file", required_argument, 0, 'f'},
        {"size", required_argument, 0, 's'},
        {"block-size", required_argument, 0, 'b'},
        {"pattern", required_argument, 0, 'p'},
        {"queue-depth", required_argument, 0, 'q'},
        {"threads", required_argument, 0, 't'},
        {"runtime", required_argument, 0, 'r'},
        {"direct", no_argument, 0, 'd'},
        {"verify", no_argument, 0, 'v'},
        {"verbose", no_argument, 0, 'V'},
        {"help", no_argument, 0, 'h'},
        {"batch-size", required_argument, 0, 'B'},
        {"polling", no_argument, 0, 'P'},
        {"output-format", required_argument, 0, 'o'},
        {"perf-benchmark", no_argument, 0, 'M'},
        {"runtime-profiling", no_argument, 0, 'R'},
        {"engine-type", required_argument, 0, 'e'},
        {0, 0, 0, 0}
    };
    
    int option_index = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "f:s:b:p:q:t:r:dvVhB:Po:MRe:", long_options, &option_index)) != -1) {
        switch (c) {
            case 'f':
                filename = optarg;
                break;
            case 's':
                file_size = std::stoull(optarg);
                if (file_size < block_size) {
                    std::cerr << "错误: 文件大小必须大于等于块大小" << std::endl;
                    return false;
                }
                break;
            case 'b':
                block_size = std::stoul(optarg);
                if (block_size == 0 || (block_size & (block_size - 1)) != 0) {
                    std::cerr << "错误: 块大小必须是2的幂次方" << std::endl;
                    return false;
                }
                break;
            case 'p':
                pattern = parse_pattern(optarg);
                break;
            case 'q':
                queue_depth = std::stoul(optarg);
                if (queue_depth == 0) {
                    std::cerr << "错误: 队列深度必须大于0" << std::endl;
                    return false;
                }
                break;
            case 't':
                num_threads = std::stoul(optarg);
                if (num_threads == 0) {
                    std::cerr << "错误: 线程数必须大于0" << std::endl;
                    return false;
                }
                break;
            case 'r':
                runtime_seconds = std::stoul(optarg);
                break;
            case 'd':
                direct_io = true;
                break;
            case 'v':
                verify_data = true;
                break;
            case 'V':
                verbose = true;
                break;
            case 'B':
                batch_size = std::stoul(optarg);
                if (batch_size == 0) {
                    std::cerr << "错误: 批量大小必须大于0" << std::endl;
                    return false;
                }
                break;
            case 'P':
                use_polling = true;
                break;
            case 'o':
                output_format = optarg;
                if (output_format != "text" && output_format != "json" && output_format != "csv") {
                    std::cerr << "错误: 输出格式必须是 text, json 或 csv" << std::endl;
                    return false;
                }
                break;
            case 'M':
                enable_perf_benchmark = true;
                break;
            case 'R':
                enable_runtime_profiling = true;
                break;
            case 'e':
                engine_type = parse_engine_type(optarg);
                break;
            case 'h':
                print_help();
                return false;
            case '?':
                return false;
            default:
                return false;
        }
    }
    
    // 性能基准测试不需要文件名
    if (filename.empty() && !enable_perf_benchmark) {
        std::cerr << "错误: 必须指定文件名或设备名" << std::endl;
        return false;
    }
    
    return true;
}

void Config::print_help() const {
    std::cout << "用法: aio_bench [选项]\n\n"
              << "选项:\n"
              << "  -f, --file FILE          测试文件或块设备路径 (必需)\n"
              << "  -s, --size SIZE          文件大小 (默认: 1GB)\n"
              << "  -b, --block-size SIZE    IO块大小 (默认: 4096)\n"
              << "  -p, --pattern PATTERN    IO模式: rand_read, rand_write, rand_rw, seq_read, seq_write (默认: rand_rw)\n"
              << "  -q, --queue-depth DEPTH  队列深度 (默认: 32)\n"
              << "  -t, --threads NUM        线程数 (默认: 1)\n"
              << "  -r, --runtime SEC        运行时间秒数 (默认: 30)\n"
              << "  -d, --direct             使用Direct IO (默认启用)\n"
              << "  -v, --verify             验证数据正确性\n"
              << "  -V, --verbose            详细输出\n"
              << "  -B, --batch-size SIZE    批量提交大小 (默认: 16)\n"
              << "  -P, --polling            使用轮询模式\n"
              << "  -o, --output-format FMT  输出格式: text, json, csv (默认: text)\n"
              << "  -M, --perf-benchmark     启用性能分析模式 (使用nanobench分析AIO测试性能)\n"
              << "  -R, --runtime-profiling  启用运行时性能分析\n"
              << "  -e, --engine-type TYPE   指定引擎类型: libaio, io_uring (默认: libaio)\n"
              << "  -h, --help               显示帮助信息\n\n"
              << "示例:\n"
              << "  aio_bench -f /dev/nvme0n1 -p rand_read -q 64 -t 4 -r 60\n"
              << "  aio_bench -f test.dat -s 1G -p rand_rw -b 4096 -d\n"
              << std::endl;
}

void Config::print_config() const {
    std::cout << "=== 配置信息 ===" << std::endl;
    std::cout << "文件/设备: " << filename << std::endl;
    std::cout << "文件大小: " << file_size << " 字节" << std::endl;
    std::cout << "块大小: " << block_size << " 字节" << std::endl;
    std::cout << "IO模式: ";
    switch (pattern) {
        case IOPattern::RANDOM_READ: std::cout << "随机读"; break;
        case IOPattern::RANDOM_WRITE: std::cout << "随机写"; break;
        case IOPattern::RANDOM_READ_WRITE: std::cout << "随机读写"; break;
        case IOPattern::SEQUENTIAL_READ: std::cout << "顺序读"; break;
        case IOPattern::SEQUENTIAL_WRITE: std::cout << "顺序写"; break;
    }
    std::cout << std::endl;
    std::cout << "队列深度: " << queue_depth << std::endl;
    std::cout << "线程数: " << num_threads << std::endl;
    std::cout << "运行时间: " << runtime_seconds << " 秒" << std::endl;
    std::cout << "Direct IO: " << (direct_io ? "启用" : "禁用") << std::endl;
    std::cout << "数据验证: " << (verify_data ? "启用" : "禁用") << std::endl;
    std::cout << "批量大小: " << batch_size << std::endl;
    std::cout << "轮询模式: " << (use_polling ? "启用" : "禁用") << std::endl;
    std::cout << "输出格式: " << output_format << std::endl;
    std::cout << "引擎类型: ";
    switch (engine_type) {
        case EngineType::LIBAIO: std::cout << "libaio"; break;
        case EngineType::IO_URING: std::cout << "io_uring"; break;
    }
    std::cout << std::endl;
    std::cout << "===============" << std::endl;
}

IOPattern Config::parse_pattern(const std::string& pattern_str) const {
    std::string lower_pattern = pattern_str;
    std::transform(lower_pattern.begin(), lower_pattern.end(), lower_pattern.begin(), ::tolower);
    
    if (lower_pattern == "rand_read" || lower_pattern == "random_read") {
        return IOPattern::RANDOM_READ;
    } else if (lower_pattern == "rand_write" || lower_pattern == "random_write") {
        return IOPattern::RANDOM_WRITE;
    } else if (lower_pattern == "rand_rw" || lower_pattern == "random_rw") {
        return IOPattern::RANDOM_READ_WRITE;
    } else if (lower_pattern == "seq_read" || lower_pattern == "sequential_read") {
        return IOPattern::SEQUENTIAL_READ;
    } else if (lower_pattern == "seq_write" || lower_pattern == "sequential_write") {
        return IOPattern::SEQUENTIAL_WRITE;
    } else {
        std::cerr << "警告: 未知的IO模式 '" << pattern_str << "', 使用默认模式 random_rw" << std::endl;
        return IOPattern::RANDOM_READ_WRITE;
    }
}

EngineType Config::parse_engine_type(const std::string& engine_str) const {
    std::string lower_engine = engine_str;
    std::transform(lower_engine.begin(), lower_engine.end(), lower_engine.begin(), ::tolower);
    
    if (lower_engine == "libaio" || lower_engine == "aio") {
        return EngineType::LIBAIO;
    } else if (lower_engine == "io_uring" || lower_engine == "uring") {
        return EngineType::IO_URING;
    } else {
        std::cerr << "警告: 未知的引擎类型 '" << engine_str << "', 使用默认引擎 libaio" << std::endl;
        return EngineType::LIBAIO;
    }
}

} // namespace aio_bench 