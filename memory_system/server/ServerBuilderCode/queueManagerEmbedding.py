import logging
import torch.nn.functional as F
from queue import Empty  # Import Empty exception directly
import numpy as np
from queue import Queue, Full
import threading
from threading import Lock
import uuid
import time
from dataclasses import dataclass
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
@dataclass
class EmbeddingRequest:
    id: str
    text: str
    timestamp: float
    priority: int = 0

class QueueFullException(Exception):
    pass

class EmbeddingQueueManager:
    """Enhanced queue manager with better error handling and monitoring"""
    def __init__(
        self, 
        embedding_model, 
        batch_size=16, 
        max_wait_time=0.1, 
        max_queue_size=1000,
        result_timeout=300
    ):
        self.queue = Queue(maxsize=max_queue_size)
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.results: Dict[str, Any] = {}
        self.results_lock = Lock()
        self.result_timeout = result_timeout
        self.stats = {
            "processed_requests": 0,
            "failed_requests": 0,
            "average_batch_size": []
        }
        self.stats_lock = Lock()
        
        # Start processing and cleanup threads
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_results, daemon=True)
        self.processing_thread.start()
        self.cleanup_thread.start()

    def add_request(self, text: str, priority: int = 0) -> str:
        """Add a new embedding request to the queue with priority"""
        request_id = str(uuid.uuid4())
        try:
            request = EmbeddingRequest(
                id=request_id,
                text=text,
                timestamp=time.time(),
                priority=priority
            )
            self.queue.put(request, timeout=1)
            return request_id
        except Full:
            raise QueueFullException("Embedding queue is full")

    def get_result(self, request_id: str, timeout=30) -> Dict[str, Any]:
        """Get result with timeout and thread-safe access"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.results_lock:
                if request_id in self.results:
                    return self.results.pop(request_id)
            time.sleep(0.1)
        return {"error": "Request timed out", "status": "error"}

    def _cleanup_old_results(self):
        """Periodically clean up old results"""
        while self.running:
            time.sleep(60)  # Clean up every minute
            current_time = time.time()
            with self.results_lock:
                expired = [
                    rid for rid, result in self.results.items()
                    if current_time - result.get('timestamp', 0) > self.result_timeout
                ]
                for rid in expired:
                    del self.results[rid]
                    logger.warning(f"Cleaned up expired result {rid}")

    def _process_queue(self):
        """Process requests in batches with improved error handling"""
        while self.running:
            batch: List[EmbeddingRequest] = []
            batch_texts: List[str] = []
            
            # Collect batch
            start_time = time.time()
            while len(batch) < self.batch_size and time.time() - start_time < self.max_wait_time:
                try:
                    request = self.queue.get_nowait()
                    batch.append(request)
                    batch_texts.append(request.text)
                except Empty:  # Use the imported Empty exception
                    if batch:
                        break
                    time.sleep(0.01)
                    continue

            if not batch:
                continue

            # Process batch
            try:
                embeddings = self.embedding_model.get_text_embeddings(
                    texts=batch_texts,
                    normalize=True
                )
                
                # Store results
                with self.results_lock:
                    for idx, request in enumerate(batch):
                        self.results[request.id] = {
                            "embedding": embeddings[idx].tolist(),
                            "status": "success",
                            "timestamp": time.time()
                        }
                
                # Update stats
                with self.stats_lock:
                    self.stats["processed_requests"] += len(batch)
                    self.stats["average_batch_size"].append(len(batch))
                    if len(self.stats["average_batch_size"]) > 100:
                        self.stats["average_batch_size"].pop(0)
                
            except Exception as e:
                logger.error(f"Batch processing error: {str(e)}")
                with self.results_lock:
                    for request in batch:
                        self.results[request.id] = {
                            "error": str(e),
                            "status": "error",
                            "timestamp": time.time()
                        }
                with self.stats_lock:
                    self.stats["failed_requests"] += len(batch)
                    

    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        with self.stats_lock:
            stats = self.stats.copy()
            if stats["average_batch_size"]:
                stats["average_batch_size"] = np.mean(stats["average_batch_size"])
            else:
                stats["average_batch_size"] = 0
        return stats

    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        self.processing_thread.join(timeout=5)
        self.cleanup_thread.join(timeout=5)