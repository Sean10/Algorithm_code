import multiprocessing

# 基础配置
bind = "127.0.0.1:5099"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000

# 优化配置
backlog = 2048
max_requests = 5000
max_requests_jitter = 500
keepalive = 5

# 超时设置
timeout = 30
graceful_timeout = 30

# 日志设置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程命名
proc_name = "gunicorn_flask"

# 并发优化
preload_app = True
reuse_port = True