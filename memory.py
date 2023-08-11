import psutil
from time import sleep
from subprocess import Popen

process_pid = int(input("PID: "))  # Replace with the desired process PID
while True:
  try:
    process = psutil.Process(process_pid)
    memory_info = process.memory_info()

    # Memory usage in bytes
    rss_memory = memory_info.rss / 1048576

    print(f"Resident Set Size (RSS) Memory: {rss_memory} MB")
    sleep(1)
  except psutil.NoSuchProcess:
    print("Process completed")
    break