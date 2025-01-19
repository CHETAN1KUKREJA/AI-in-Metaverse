import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from typing import Dict, Any, Optional

class QuantizedPlanner:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-14B-Instruct-AWQ"):
        """
        Initialize the Quantized Planner with Qwen 2.5 model.
        
        Args:
            model_name (str): Name or path of the model to load
        """
        self.model_name = model_name
        self.setup_model()
    
    def clean_response(self, response: str) -> Dict[str, Any]:
        """
        Clean and extract JSON from the model's response.
        
        Args:
            response (str): Raw response from the model
            
        Returns:
            Dict: Cleaned JSON or error dictionary
        """
        try:
            # Find JSON boundaries
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                return json.loads(json_str)
                
            return {"error": "No valid JSON found", "plan": {}}
            
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format", "plan": {}}
    
    def setup_model(self) -> None:
        """Set up the Qwen model and tokenizer."""
        try:
            # Load model with Qwen-specific configurations
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True
            )
            
            # Load Qwen tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup Qwen model: {str(e)}")
    
    def plan_memory(self, user_input: str) -> Dict[str, Any]:
        """
        Generate a plan based on the provided input using Qwen model.
        
        Args:
            user_input (str): Input text to generate plan from
            
        Returns:
            Dict[str, Any]: Generated plan or error information
        """
        try:
            # Prepare messages using Qwen's chat template
            messages = [
                {
                    "role": "system",
                    "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            
            # Apply chat template
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Prepare inputs
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.1
            )
            
            # Process generated ids
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            # Decode response
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]            
            # Clean and parse response
            # print(self.clean_response(response))
            return self.clean_response(response)
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "plan": {},
                "raw_response": response if 'response' in locals() else None
            }
            return error_response