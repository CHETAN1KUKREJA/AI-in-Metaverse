from backend.planer import Planer
from backend.summarizer import Summarizer
import json

class LLM:
    def __init__(self, planer_model_path, summarizer_model_path):
        self.planer = Planer(planer_model_path)
        self.summarizer = Summarizer(summarizer_model_path)
        
        self.memory = []
        
    def update_memory(self, call_batch):
        call = call_batch[0]
        match call["name"]:
            case "go_to":
                # mem = f"You go to {call['arguments']['location']}, the reason is: {call['arguments']['explanation_for_this_action_and_arguments']}"
                mem = f"You go to {call['arguments']['location']}."
                self.memory.append(mem)
            case "enter":
                mem = f"You enter {call['arguments']['location']}."
                self.memory.append(mem)
            case "talk":
                mem = f"You try to talk with \"{call['arguments']['other_agent']}\". But \"{call['arguments']['other_agent']}\" doesn't exist here!"
                self.memory.append(mem)
            case "exit":
                mem = f"You exit. Now you are outside again."
                self.memory.append(mem)
        
    def iterate_step(self, input_jsons):
        response_batch = self.planer.iterate_step(input_jsons, self.memory)
        call_batch = self.summarizer.iterate_step(response_batch)
        self.update_memory(call_batch)
        return call_batch