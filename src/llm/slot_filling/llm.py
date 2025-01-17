from .planer import Planer
from .summarizer import LLMSummarizer, PatternSummarizer
import json


# Qwen/Qwen2.5-7B-Instruct
# Qwen/Qwen2.5-14B-Instruct
# unsloth/Qwen2.5-14B-Instruct-bnb-4bit
# Qwen/Qwen2.5-14B-Instruct-AWQ

class LLM:
    def __init__(self, planer_model_path="Qwen/Qwen2.5-14B-Instruct-AWQ", summarizer_model_path=None, multi_step=False):
        self.planer = Planer(planer_model_path, multi_step=multi_step)
        self.summarizer = LLMSummarizer(
            summarizer_model_path) if summarizer_model_path is not None else PatternSummarizer()

        self.memory = []

    def update_memory(self, call_batch):
        calls = call_batch[0]
        calls = calls['actions']
        for call in calls:
            match call["function_name"]:
                case "goTo":
                    mem = f"You go to {call['parameters']['target_name']}. Now you are near to it, but still not in it."
                case "talk":
                    mem = f"You try to talk with \"{call['parameters']['target_name']}\". But \"{call['parameters']['target_name']}\" doesn't exist here!"
                case "take":
                    mem = f"You just toke {call['parameters']['amount']} of {call['parameters']['target_name']} from nearby."
                case "drop":
                    mem = f"You just dropped {call['parameters']['amount']} of {call['parameters']['target_name']} from nearby."
                

            self.memory.append(mem)

    def iterate_step(self, input_jsons):
        (action_batch, reason_batch) = self.planer.iterate_step(input_jsons, self.memory)
        call_batch = self.summarizer.iterate_step(action_batch, input_jsons)
        self.update_memory(call_batch)
        return (call_batch, reason_batch)

    """
    Processes the given JSON requests and the current corresponding memories, performing a single iteration
    step for the LLM. It updates the memories accordingly and returns the resulting call and reason
    batches.
    Args:
        requests (list of JSON): The input data specifying the requests to be processed by the LLM.
        memory: The current memories representing historical context or events.
    Returns:
        tuple: A tuple containing two elements:
            - call_batch: The generated actions (calls) determined by the LLM.
            - reason_batch: The explanations or justifications for the generated actions.
    """
    def process(self, requests, memories):
        return self.iterate_step(requests)
    # TODO: Implement memory usage
