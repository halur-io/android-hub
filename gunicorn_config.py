# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = 1
timeout = 300  # 5 minutes for AI image processing
worker_class = "sync"
reload = True
reuse_port = True
loglevel = "info"
graceful_timeout = 300
