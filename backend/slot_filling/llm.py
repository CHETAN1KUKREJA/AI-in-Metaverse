from backend.slot_filling.planer import Planer
from backend.slot_filling.summarizer import LLMSummarizer, PatternSummarizer
import json

# Qwen/Qwen2.5-7B-Instruct
# Qwen/Qwen2.5-14B-Instruct
# unsloth/Qwen2.5-14B-Instruct-bnb-4bit
# Qwen/Qwen2.5-14B-Instruct-AWQ

class LLM:
    def __init__(self, planer_model_path="Qwen/Qwen2.5-14B-Instruct-AWQ", summarizer_model_path=None, multi_step = False):
        self.planer = Planer(planer_model_path, multi_step=multi_step)
        self.summarizer = LLMSummarizer(summarizer_model_path) if summarizer_model_path is not None else PatternSummarizer()
        
        self.memory = []
        
    def update_memory(self, call_batch):
        calls = call_batch[0]
        for call in calls:
            match call["name"]:
                case "go_to":
                    mem = f"You go to {call['arguments']['location']}. Now you are near to it, but still not in it."
                case "talk":
                    mem = f"You try to talk with \"{call['arguments']['other_agent']}\". But \"{call['arguments']['other_agent']}\" doesn't exist here!"
                case "take":
                    mem = f"You just toke {call['arguments']['amount']} of {call['arguments']['objectName']} from nearby."
                case "drop":
                    mem = f"You just dropped {call['arguments']['amount']} of {call['arguments']['objectName']} from nearby."
            
            self.memory.append(mem)
        
    def iterate_step(self, input_jsons):
        response_batch = self.planer.iterate_step(input_jsons, self.memory)
        call_batch = self.summarizer.iterate_step(response_batch)
        self.update_memory(call_batch)
        return call_batch