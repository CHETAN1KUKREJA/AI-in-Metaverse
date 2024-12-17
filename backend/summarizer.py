import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from input_processing.actions import tools
import regex
import json


class Summarizer:
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
