import threading
from backend.slot_filling.llm import LLM

class WorkerAgent():
    id_counter = 0
    
    def __init__(self, id):
        self.llm = LLM()
        self.worker_id = id
        
    def process(self, request, memory):
        return self.llm.process(request, memory)
    

class WorkersPool():
    def __init__(self, num_workers = 1):
        self.workers = []
        for i in range(num_workers):
            self.workers.append(WorkerAgent(self, i))
        self.empty_sem = threading.Semaphore(num_workers)    
        
    def process(self, request, memory):
        self.empty_sem.acquire()
        worker = self.workers.pop()
        
        result = worker.process(request, memory)
        
        self.workers.append(worker)
        self.empty_sem.release()

        return result
        