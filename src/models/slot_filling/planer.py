import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from src.promts.prompt_slot_filling import get_prompt


class Planer:
    def __init__(self, model_path: str, cache_dir="cached_models", multi_step=False):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=cache_dir)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            cache_dir=cache_dir,
            device_map="auto",
            torch_dtype="auto",
            attn_implementation="flash_attention_2"
        )
        
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
            top_p=0.8,
            temperature=0.3,
        )

        generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(input_ids_batch, output_ids_batch)]
        response_batch = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
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
        print(response_batch[0])
        return action_batch
