import json
import re
import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, logging
from langchain_experimental.llms import JsonFormer
from huggingface_hub import login, HfApi
import os


action_schemas = {
            "talk": {
                "type": "object",
                "properties": {
                    "volume": {"type": "string", "enum": ["quiet", "normal", "loud"]},
                    "content": {"type": "string"}
                }
            },
            "take": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "amount": {"type": "number"}
                }
            },
            "drop": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "amount": {"type": "number"}
                }
            }
            # Add more action schemas as needed
        }

examples = {
            "talk": {
                "query": "I want to ask Maria what she has to trade",
                "response": {
                    "action": "talk",
                    "action_input": {
                        "volume": "normal",
                        "content": "Hello Maria, what do you have to trade?"
                    }
                }
            },
            "take": {
                "query": "I want to take 5 apples",
                "response": {
                    "action": "take",
                    "action_input": {
                        "item": "apples",
                        "amount": 5
                    }
                }
            },
        }
        
prompt_template = """You must respond using JSON format, with a single action and single action input. You have to read the entire human query and most of the time the output is given between '<toolcall> </toolcall>' 
          but if you dont find this you can select one action from the list that is stated in the query
          There may be a lot of Thought process in the query you dont have to get swayed by that and focus on the action and action and action input.
          Available actions: {actions}
          EXAMPLES:
          {formatted_examples}
          BEGIN! Parse the following request into an appropriate action:
          Human: {query}
          Assistant:
        """

def generate_prompt(query,available_actions=None):
        """Generate a prompt with examples for available actions"""
        if available_actions is None:
            available_actions = list(action_schemas.keys())

        formatted_examples = "\n".join(
            f"Human: {ex['query']}\n"
            f"Assistant: {ex['response']}\n"
            for action in available_actions
            if action in examples
            for ex in [examples[action]]
        )
        return prompt_template.format(
            actions=", ".join(available_actions),
            formatted_examples=formatted_examples,
            query=query  # Will be filled in during parse_action
        )


def get_decoder_schema(available_actions=None):
        """
        Generate a decoder schema based on available actions
        
        Args:
            available_actions (list): List of action names that are currently available
        """
        if available_actions is None:
            available_actions = list(action_schemas.keys())
            
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": available_actions
                },
                "action_input": {
                    "type": "object",
                    "oneOf": [
                        {
                            "if": {"properties": {"action": {"const": action}}},
                            "then": action_schemas[action]
                        }
                        for action in available_actions
                    ]
                }
            }
        }

def clean_jsonformer_response(response, prompt_string):
    # Strip leading/trailing spaces from the prompt string and response
    prompt_string = prompt_string.strip()
    response = response.strip()

    # Check if the response starts with the prompt string and remove it
    if response.startswith(prompt_string):
        response = response[len(prompt_string):].strip()

    # Return the cleaned response
    return response


def extractor_RE(text):
    """
    Extract JSON from LLM output that may be contained within XML-like tags
    or other formatting. Handles multiple potential formats and validates JSON.
    
    Args:
        text (str): The raw text output from the LLM
        
    Returns:
        list: List of dictionaries containing:
            - 'json': The extracted JSON object or None if invalid
            - 'raw': The raw extracted JSON string
            - 'error': Error message if JSON is invalid, None otherwise
    """
    # List to store all potential JSON matches
    extracted = []
    
    # Common patterns we might encounter
    patterns = [
        # Match content between <tool_call> tags
        r'<tool_call>(.*?)</tool_call>',
        # Match anything that looks like JSON object
        # r'\{[^{}]*\}',
        # Match content between ```json and ``` (for markdown)
        r'```json\s*(.*?)\s*```',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            raw_json = match.group(1) if len(match.groups()) > 0 else match.group(0)
            
            # Clean up the extracted text
            raw_json = raw_json.strip()
            
            # Skip if it's clearly not JSON
            if not (raw_json.startswith('{') and raw_json.endswith('}')):
                continue
                
            try:
                parsed_json = json.loads(raw_json)
                extracted.append({
                    'json': parsed_json,
                    'raw': raw_json,
                    'error': None
                })
            except json.JSONDecodeError as e:
                extracted.append({
                    'json': None,
                    'raw': raw_json,
                    'error': str(e)
                })
    
    return extracted

def extractor_Jsonformer(text, model_name="google/gemma-2b-it", available_actions=None, device=None):
    try:
        # Determine device automatically if not specified
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Check if Hugging Face login is needed
        api = HfApi()
        try:
            api.whoami()  # Check if already logged in
        except Exception:
            # Prompt for Hugging Face token if not logged in
            token = os.getenv("HF_TOKEN") or input("Please enter your Hugging Face token: ")
            login(token)

        # Load the model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # Create a Hugging Face pipeline
        hf_model = pipeline(
            "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=2048, device=device
        )

        # Initialize JsonFormer and generate the response
        json_former = JsonFormer(json_schema=get_decoder_schema(available_actions), pipeline=hf_model)
        results = json_former.predict(generate_prompt(text, available_actions), stop=["Observation:", "Human:"])

        # Clean the response if it contains the input prompt
        clean_results = clean_jsonformer_response(results, generate_prompt(text, available_actions))

        return json.dumps(clean_results)

    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({"error": str(e)})
