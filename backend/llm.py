import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from input_processing import get_processed
import regex
import json


class LLM:
    def __init__(self, model_path: str, cache_dir="cached_models"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=cache_dir)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            cache_dir=cache_dir,
            device_map="auto",
            torch_dtype="auto",
        )
        
        self.memory = []

    def preprocess_input(self, input_jsons):
        prompt_batch, action_tools_batch = [], []
        for input_json in input_jsons:
            prompt, action_tools = get_processed(input_json)
            if len(self.memory) > 0:
                prompt += "\n\nYou performed actions:\n"
                for mem in self.memory:
                    prompt += mem + "\n"
            prompt_batch.append(prompt)
            # print(prompt)
            action_tools_batch.append(action_tools)
        return prompt_batch, action_tools_batch

    def generate_step(self, prompt_batch, action_tools_batch):
        inputs_batch = []

        for prompt, action_tools in zip(prompt_batch, action_tools_batch):
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "What should you do? Only output the tool call!"},
            ]
            inputs_batch.append(
                self.tokenizer.apply_chat_template(
                    messages,
                    tools=action_tools,
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
            max_new_tokens=2048,
            do_sample=True,
            top_p=0.9,
            temperature=0.6,
        )

        generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(input_ids_batch, output_ids_batch)]
        response_batch = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return response_batch

    def postprocess_output(self, response_batch):
        call_batch = []
        pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        for response in response_batch:
            tool_call = pattern.findall(response)
            call_batch.append(tool_call[0] if len(tool_call) > 0 else None)
        return call_batch

    def update_memory(self, call_batch):
        call = json.loads(call_batch[0])
        match call["name"]:
            case "go_to":
                # mem = f"You go to {call['arguments']['location']}, the reason is: {call['arguments']['explanation_for_this_action_and_arguments']}"
                mem = f"You go to {call['arguments']['location']}"
                self.memory.append(mem)

    def iterate_step(self, input_json):
        prompt_batch, action_tools_batch = self.preprocess_input(input_json)
        response_batch = self.generate_step(prompt_batch, action_tools_batch)
        call_batch = self.postprocess_output(response_batch)
        self.update_memory(call_batch)
        return call_batch
