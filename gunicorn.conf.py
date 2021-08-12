import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
# max-requests-jitter INT