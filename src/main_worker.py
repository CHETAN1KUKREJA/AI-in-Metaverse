from llm import WorkerService
import argparse

def start_worker():
    parser = argparse.ArgumentParser(description="Start a worker service")
    parser.add_argument("--registry-host", default="localhost", help="Registry host")
    parser.add_argument("--registry-port", type=int, default=33455, help="Registry port")
    parser.add_argument("--worker-host", type=str, help="Worker Host")
    parser.add_argument("--worker-port", type=int, required=True, help="Worker port")

    args = parser.parse_args()

    worker = WorkerService(args.registry_host, args.registry_port, args.worker_host, args.worker_port, heartbeat_diff_time=4.0)
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()
    
    print("========== Initializing Workers ==========")
    worker.start()

if __name__ == "__main__":
    start_worker()
    

# python src/main_distributer.py
# python src/main_worker.py --registry-host localhost --registry-port 33456 --worker-port 33457