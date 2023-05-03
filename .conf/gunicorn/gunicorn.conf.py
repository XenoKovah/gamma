import os
import multiprocessing


# Default to be between 2-4 workers per core in the server
# Can be overriten via env export GUNICORN_WORKERS=n
workers = multiprocessing.cpu_count() * 2 + 1


for k, v in os.environ.items():
    if k.startswith("GUNICORN_"):
        key = k.split('_', 1)[1].lower()
        locals()[key] = v
