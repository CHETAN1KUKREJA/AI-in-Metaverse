import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from src.promts import tools
import regex
import json
import re


class LLMSummarizer:
    def __init__(self, model_path: str, cache_dir="cached_models"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=cache_dir)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            cache_dir=cache_dir,
            device_map="auto",
            torch_dtype="auto",
        )

    def summarize_step(self, inputs):
        inputs_batch = []

        for prompt in inputs:
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Given \n" + prompt + "\n"},
                {"role": "user", "content": "What should you do? Output the tool call."},
            ]
            inputs_batch.append(
                self.tokenizer.apply_chat_template(
                    messages,
                    tools=tools,
                    add_generation_prompt=True,
                    return_tensors="pt",
                    tokenize=False,
                )
            )

        inputs_batch = self.tokenizer(inputs_batch)
        input_ids_batch = torch.tensor(inputs_batch["input_ids"]).to(self.model.device)
        attn_mask_batch = torch.tensor(inputs_batch["attention_mask"]).to(self.model.device)

        output_ids_batch = self.model.generate(
            input_ids_batch,
            attention_mask=attn_mask_batch,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.3,
        )

        generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(input_ids_batch, output_ids_batch)]
        response_batch = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return response_batch

    def postprocess(self, response_batch):
        call_batch = []
        pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        for response in response_batch:
            tool_call = pattern.findall(response)
            call_batch.append(json.loads(tool_call[0]) if len(tool_call) > 0 else None)
        return call_batch

    def iterate_step(self, inputs):
        response_batch = self.summarize_step(inputs)
        call_batch = self.postprocess(response_batch)
        print(call_batch[0])
        return call_batch


class PatternSummarizer:
    
    def parse_action(self, text, actor_name): # TODO change the direct parameter of actor_name to a smarter way to pass this data!!!!
        text = text.strip().replace("Action: ", "")
        actions = [t.strip() for t in text.split(",")]
        
        patterns = {
            "goTo": {
                "pattern": r"goTo\s+(\w+)",
                "fields": ["target_name"],
            },
            "take": {
                "pattern": r"take\s+(\d+)\s+of\s+(\w+)",
                "fields": ["amount", "target_name"],
            },
            "drop": {
                "pattern": r"drop\s+(\d+)\s+of\s+(\w+)",
                "fields": ["amount", "target_name"],
            },
            "talk1": {
                "function_name": "talk",
                "pattern": r"talk\s+to\s+(\w+)\s+with\s+\"(\w+)\"",
                "fields": ["target_name", "message"]
            },
            "talk2": {
                "function_name": "talk",
                "pattern": r"talk\s+to\s+(\w+)\s+with\s+\'(\w+)\'",
                "fields": ["target_name", "message"]
            }
        }

        output = []

        for action in actions:
            for action_type, config in patterns.items():
                match = re.search(config["pattern"], action)
                result = None
                if match:
                    action_name = config["function_name"] if "function_name" in config else action_type
                    result = {"function_name": action_name, "parameters": {}, "actor_name": ""}
                    for i, field in enumerate(config["fields"]):
                        result["parameters"][field] = match.group(i + 1)
                    result["actor_name"] = actor_name
                    break
                
            if result:
                output.append(result)
            else:
                return {"actions": output}

        return {"actions": output}

    def iterate_step(self, inputs, input_jsons):
        call_batch = []
        for i, input_item in enumerate(inputs):
            call_batch.append(self.parse_action(input_item, input_jsons[i]["agent"]["name"]))
        return call_batch
