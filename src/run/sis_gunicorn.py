"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

# Gunicorn configuration file

# Process settings
daemon = True  # Run in background
bind = '0.0.0.0:33333'  # Bind address and port
pidfile = '/var/run/sis_gunicorn.pid'  # Process ID file
chdir = '/opt/pythonService/spider-image-system/run'  # Working directory

# Worker settings
worker_class = 'uvicorn.workers.UvicornWorker'  # Use Uvicorn worker class for ASGI
workers = 1  # Number of worker processes
threads = 2  # Threads per worker
worker_connections = 2000  # Max concurrent connections

# Logging
loglevel = 'debug'  # Log level for error logs
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  # Access log format
accesslog = "/opt/pythonService/spider-image-system/fastapi_log/gunicorn_access.log"  # Access log path
errorlog = "/opt/pythonService/spider-image-system/fastapi_log/gunicorn_error.log"  # Error log path
