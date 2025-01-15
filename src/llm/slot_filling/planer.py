import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from vllm import LLM, SamplingParams
from src.promts import get_prompt


class Planer:
    def __init__(self, model_path: str, cache_dir="cached_models", multi_step=False):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=cache_dir)

        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=512)

        self.model = LLM(model=model_path, gpu_memory_utilization=1.0, tensor_parallel_size=2, disable_custom_all_reduce=True, enforce_eager=True)
        
        self.multi_step = multi_step

    def preprocess(self, input_jsons, performed_actions):
        prompt_batch = []
        for input_json in input_jsons:
            prompt = get_prompt(input_json, multi_step=self.multi_step)

            if len(performed_actions) > 0:
                prompt += "\n\nHere are your performed actions in previos steps:\n"
                for idx, mem in enumerate(performed_actions):
                    prompt += str(idx + 1) + ". " + mem + "\n"
            prompt_batch.append(prompt)

        return prompt_batch

    def generate_step(self, prompt_batch):
        inputs_batch = []

        for prompt in prompt_batch:
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "What should you do for the next step? Pay attention to what you have done until now!"},
            ]
            inputs_batch.append(
                self.tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    # return_tensors="pt",
                    tokenize=False,
                )
            )

        # inputs_batch = self.tokenizer(inputs_batch)
        # input_ids_batch = torch.tensor(inputs_batch["input_ids"]).to(self.model.device)

        outputs = self.model.generate(
            inputs_batch,
            self.sampling_params
        )

        # generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(input_ids_batch, output_ids_batch)]
        # response_batch = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        
        response_batch = []
        for output in outputs:
            response = output.outputs[0].text
            response_batch.append(response)               
        
        return response_batch

    def postprocess(self, response_batch):
        action_batch = []
        for response in response_batch:
            action = response.strip().split("\n")[-1]
            action_batch.append(action)
        return action_batch

    def iterate_step(self, input_jsons, performed_actions=[]):
        prompt_batch = self.preprocess(input_jsons, performed_actions)
        response_batch = self.generate_step(prompt_batch)
        action_batch = self.postprocess(response_batch)
        return (action_batch, response_batch)
