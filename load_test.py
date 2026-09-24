import requests
import time
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/predict"

TOTAL_REQUESTS = 5000
CONCURRENCY = 200


def send_request(i):
    start = time.perf_counter()

    response = requests.post(
        URL,
        json={"value": i}
    )

    latency = (time.perf_counter() - start) * 1000

    return response.status_code, latency


start_test = time.perf_counter()

with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
    results = list(
        executor.map(send_request, range(TOTAL_REQUESTS))
    )

total_time = time.perf_counter() - start_test

successful = sum(
    1 for status, _ in results if status == 200
)

average_latency = sum(
    latency for _, latency in results
) / len(results)

print(f"Total requests: {TOTAL_REQUESTS}")
print(f"Successful requests: {successful}")
print(f"Concurrency: {CONCURRENCY}")
print(f"Total time: {total_time:.2f} seconds")
print(f"Throughput: {TOTAL_REQUESTS / total_time:.2f} req/s")
print(f"Average client latency: {average_latency:.2f} ms")