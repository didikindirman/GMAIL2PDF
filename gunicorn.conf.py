# Gunicorn configuration file for Render deployment

# Number of worker processes. A general rule is (2 * $num_cores) + 1.
# Render's smallest instance usually has 1 or 2 vCPUs.
# We'll set it to 4 to be safe and responsive.
workers = 4

# Use an efficient worker class for asynchronous handling (gevent is good for I/O)
# WeasyPrint can be CPU-intensive, so 'sync' workers are often simpler/more reliable.
worker_class = 'sync' 

# Listen on the port specified by the environment variable $PORT
bind = '0.0.0.0:8080' # Use 8080 as a standard default for Render/Docker

# Log levels
loglevel = 'info'
accesslog = '-' # Output access logs to stdout
errorlog = '-'  # Output error logs to stdout

# Timeout for workers (in seconds). Increase if conversions take longer.
timeout = 600 # 10 minutes timeout, as EML conversion can be slow.

# Preload the application code before the worker processes fork. 
# This can save memory and speed up startup time.
preload_app = True