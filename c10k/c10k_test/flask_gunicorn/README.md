# Flask + Gunicorn C10K 测试

这是一个使用 Flask 和 Gunicorn 实现的 C10K 测试服务器。

## 安装

1. 确保您已安装 Python 3.7+。

2. 安装依赖：

   ```
   pip install -r requirements.txt
   ```

## 运行服务器

使用以下命令启动服务器：

```
gunicorn -c gunicorn_config.py app:app
```

## 性能测试

使用 Apache Benchmark (ab) 进行性能测试。如果您还没有安装 ab，可以按照以下步骤安装：

### 安装 ab

在 macOS 上：
```
brew install apache2
```

在 Ubuntu/Debian 上：
```
sudo apt-get install apache2-utils
```

### 运行测试

确保服务器正在运行，然后使用以下命令进行测试：

```bash
# 发送 10000 个请求，并发数为 1000
ab -n 10000 -c 1000 http://localhost:8000/

# 持续 30 秒，并发数为 1000
ab -t 30 -c 1000 http://localhost:8000/
```

参数说明：
- `-n`: 请求总数
- `-c`: 并发数
- `-t`: 测试持续时间（秒）

测试结果会显示重要的性能指标，包括：
- 每秒请求数 (Requests per second)
- 请求延迟 (Time per request)
- 传输速率 (Transfer rate)
- 各种响应时间百分位数