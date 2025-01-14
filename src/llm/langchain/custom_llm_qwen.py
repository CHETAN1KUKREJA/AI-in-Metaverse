import torch
from transformers.models.qwen2.modeling_qwen2 import Qwen2ForCausalLM
from transformers.models.qwen2.tokenization_qwen2_fast import Qwen2TokenizerFast
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "unsloth/Qwen2.5-14B-Instruct-bnb-4bit"
quantization_config = BitsAndBytesConfig(load_in_4bit=True)

# Load the model and tokenizer from Hugging Face
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, quantization_config=quantization_config, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

class CustomLLMQwen(LLM):
    model: Qwen2ForCausalLM
    tokenizer: Qwen2TokenizerFast

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        messages = [
            {"role": "user", "content": prompt},
        ]

        encodeds = self.tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(self.model.device)

        generated_ids = self.model.generate(
            model_inputs, max_new_tokens=512, do_sample=True, pad_token_id=tokenizer.eos_token_id, top_k=4, temperature=0.7
        )
        decoded = self.tokenizer.batch_decode(generated_ids)

        # This does not stop when meeting with a stop token ???
        print(decoded[0])
        output = decoded[0].split("[/INST]")[1].replace("</s>", "").strip()

        if stop is not None:
            for word in stop:
                output = output.split(word)[0].strip()

        while not output.endswith("```"):
            output += "`"

        return output

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model}

llm_qwen = CustomLLMQwen(model=model, tokenizer=tokenizer)