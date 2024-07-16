import threading
import random
import os
import time
from collections import deque

# Constants
LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000
BULK_WRITE_SIZE = 100

buffer = deque()
lock = threading.Lock()
not_empty = threading.Event()
producer_finished = threading.Event()

script_dir = os.path.dirname(os.path.realpath(__file__))
all_file_path = os.path.join(script_dir, "all.txt")
even_file_path = os.path.join(script_dir, "even.txt")
odd_file_path = os.path.join(script_dir, "odd.txt")

def producer():
    all_numbers = []
    for _ in range(MAX_COUNT):
        num = random.randint(LOWER_NUM, UPPER_NUM)
        with lock:
            while len(buffer) >= BUFFER_SIZE:
                lock.release()
                time.sleep(0.01)
                lock.acquire()
            buffer.append(num)
            not_empty.set()
        all_numbers.append(num)
        if len(all_numbers) >= BULK_WRITE_SIZE:
            with open(all_file_path, "a") as all_file:
                all_file.write('\n'.join(map(str, all_numbers)) + '\n')
            all_numbers = []
    if all_numbers:
        with open(all_file_path, "a") as all_file:
            all_file.write('\n'.join(map(str, all_numbers)) + '\n')
    producer_finished.set()

def consume_even():
    even_numbers = []
    while not producer_finished.is_set() or buffer:
        not_empty.wait()
        with lock:
            while buffer and buffer[-1] % 2 == 0:
                even_numbers.append(buffer.pop())
                if len(even_numbers) >= BULK_WRITE_SIZE:
                    with open(even_file_path, "a") as even_file:
                        even_file.write('\n'.join(map(str, even_numbers)) + '\n')
                    even_numbers = []
            if not buffer:
                not_empty.clear()
    if even_numbers:
        with open(even_file_path, "a") as even_file:
            even_file.write('\n'.join(map(str, even_numbers)) + '\n')

def consume_odd():
    odd_numbers = []
    while not producer_finished.is_set() or buffer:
        not_empty.wait()
        with lock:
            while buffer and buffer[-1] % 2 != 0:
                odd_numbers.append(buffer.pop())
                if len(odd_numbers) >= BULK_WRITE_SIZE:
                    with open(odd_file_path, "a") as odd_file:
                        odd_file.write('\n'.join(map(str, odd_numbers)) + '\n')
                    odd_numbers = []
            if not buffer:
                not_empty.clear()
    if odd_numbers:
        with open(odd_file_path, "a") as odd_file:
            odd_file.write('\n'.join(map(str, odd_numbers)) + '\n')

if __name__ == "__main__":
    start = time.time()

    # Initialize threads
    producer_thread = threading.Thread(target=producer)
    even_consumer_thread = threading.Thread(target=consume_even)
    odd_consumer_thread = threading.Thread(target=consume_odd)

    # Start threads
    producer_thread.start()
    even_consumer_thread.start()
    odd_consumer_thread.start()

    # Wait for threads to finish
    producer_thread.join()
    even_consumer_thread.join()
    odd_consumer_thread.join()

    end = time.time()
    
    print(f"Total execution time: {end - start:.2f} seconds.")
