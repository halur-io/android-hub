# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = 1
timeout = 120  # Increased timeout for image uploads
worker_class = "sync"
reload = True
reuse_port = True
loglevel = "info"
