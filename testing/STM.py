import heapq
import time
import random

class MemoryBlock:
    """
    Importance Score for Memory
    Factors to Calculate Importance:


    Relevance: How pertinent the information is to the agent’s current goals.
    Frequency: How often similar events or interactions occur.
    Recency: How recently the information was acquired.
    Emotional/Impactful Weight: If a memory is tied to significant outcomes.
    Agent Context: Is it tied to the agent’s identity or primary role?
    Formula Example:
    Importance Score=(w1⋅Relevance)+(w2⋅Frequency)+(w3⋅Recency)+(w4⋅Impact) text{Importance Score} = (w_1  cdot  text{Relevance}) + (w_2  cdot  text{Frequency}) + (w_3 cdot  text{Recency}) + (w_4 cdot  text{Impact})
    Adjust weights (w1,w2,w3,w4w_1, w_2, w_3, w_4) based on agent design.
    """

    def __init__(self, context, importance_weights=[0.25, 0.25, 0.25, 0.25]):
        self.frequency = random.randint(0, 10)
        self.relevance = random.randint(0, 10)
        self.recency = random.randint(0, 10)
        self.impact = random.randint(0, 10)
        self.context = context
        self.importance = self.calculate_importance()
        self.importance_weights = importance_weights
        return
    
    def calculate_importance(self):
            return (self.relevance + self.frequency + self.recency + self.impact)/4
    
    def __lt__(self, other):
        return self.importance < other.importance

class STM:
    def __init__(self, memory_capacity):
        self.memory_capacity = memory_capacity
        self.memory = []

    def recalculate_importance(self):
        # Recalculate the importance score for all memory blocks
        for i in range(len(self.memory)):
            importance, memory_block = self.memory[i]
            new_importance = memory_block.importance_score()
            self.memory[i] = (new_importance, memory_block)
        heapq.heapify(self.memory)

    def add_memory_block(self, memory_block: MemoryBlock):
        importance = memory_block.calculate_importance()
        if len(self.memory) < self.memory_capacity:
            heapq.heappush(self.memory, (importance, memory_block))
        else:
            # Only add the new block if its importance is higher than the least important block
            if importance > self.memory[0][0]:
                heapq.heappushpop(self.memory, (importance, memory_block))

    def get_memory_blocks(self):
        # Return the memory blocks sorted by importance
        return [block for _, block in sorted(self.memory, reverse=True)]

class LTM:
    def __init__(self):
        self.memory = []

    def add_memory_block(self, memory_block: MemoryBlock):
        self.memory.append(memory_block)

    def get_memory_blocks(self):
        return self.memory

# Example usage:
if __name__ == "__main__":
    random.seed(0)
    stm = STM(10)
    for i in range(15):
        block = MemoryBlock(f"data_{i}")
        stm.add_memory_block(block)
        time.sleep(0.1)  # Simulate time passing

    for block in stm.get_memory_blocks():
        print(block.context, block.importance)
    
