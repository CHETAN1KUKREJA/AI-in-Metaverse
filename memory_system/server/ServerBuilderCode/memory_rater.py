import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModel,
    pipeline,
    BitsAndBytesConfig
)
import torch.nn.functional as F
import json

class QuantizedMemoryRater:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2"):
        self.model_name = model_name
        self.setup_model()
    
    def clean_jsonformer_response(self, response, prompt_string):
        # Strip leading/trailing spaces from the prompt string and response
        prompt_string = prompt_string.strip()
        response = response.strip()

        # Remove the prompt string if it exists at the start
        if response.startswith(prompt_string):
            response = response[len(prompt_string):].strip()

        # Find the first { and last }
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = response[start_idx:end_idx + 1]
            try:
                # Validate it's proper JSON
                json_obj = json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                return """{"explanation":"encountered error","rating":5}"""
        return """{"explanation":"encountered error","rating":5}"""


    def setup_model(self):
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        # Load model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quantization_config,
            device_map="auto"  # Automatically handle device placement
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Set pad token if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Create optimized pipeline
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=512,
            torch_dtype=torch.float16,
            device_map="auto",
            temperature=0.1
        )
    
    def generate_prompt(self, memory):
        return (
            "On the scale of 1 to 10, where 1 is purely mundane "
            "(e.g., brushing teeth, making bed) and 10 is extremely poignant "
            "(e.g., a break-up, college acceptance, life), rate the likely poignancy of the "
            f"following piece of memory.\nMemory: {memory}\n"
            "Provide just your rating a single number rating:<fill_in> and a explanation in JSON format like this: "
            '{"explanation": ...,"rating":.. }'
            "provide only 1 json"
        )

    def rate_memory(self, memory):
        try:
            # Generate and parse response
            prompt = self.generate_prompt(memory)
            result = self.pipeline(prompt, max_new_tokens=512)[0]['generated_text']
            return self.clean_jsonformer_response(result, prompt)
            
        except Exception as e:
            return {"error": str(e), "memory": memory}
        