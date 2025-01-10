# %% [markdown]
# # Install Required Libraries
# Install the necessary libraries using pip.

# %%
# Install the necessary libraries using pip
!pip install langchain
!pip install accelerate
!pip install -U bitsandbytes

# %% [markdown]
# # Login to Hugging Face Hub
# Log in to Hugging Face Hub using the provided token.

# %%
from huggingface_hub import login

# Replace 'your_token_here' with your Hugging Face access token
token_sukhvansh = "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"

# Log in to Hugging Face Hub
login(token_sukhvansh)

print("Successfully logged in to Hugging Face Hub!")

# %% [markdown]
# # Import Required Libraries
# Import the necessary libraries, including langchain, transformers, and others.

# %%
# Import the necessary libraries
from langchain.tools import BaseTool, StructuredTool, tool
import warnings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers.models.mistral.modeling_mistral import MistralForCausalLM
from transformers.models.llama.tokenization_llama_fast import LlamaTokenizerFast
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Mapping, Any

# %% [markdown]
# # Define Tools
# Define the tools that will be used in the environment, such as goto, talk, trade, eat, and collect_apples.

# %%
from langchain.tools import tool

@tool
def goto(location: str, speed: int) -> str:
    """Go to a specific location in the environment.
    
    Args:
        location: The target location to go to. Must be a valid location in the environment.
        speed: The speed at which you want to travel to the location.
    """
    return "Reached the location."

@tool
def talk(agent_name: str, message: str) -> str:
    """Talk to another agent.
    
    Args:
        agent_name: Name of the agent you want to communicate to.
        message: The message you want to communicate to the other agent.
    """
    return "Message communicated."

@tool
def trade(agent_name: str, amount_of_money: int, amount_of_apples: int) -> int:
    """Trade with another agent.
    
    Args:
        agent_name: The name of the agent to trade with.
        amount_of_money: Amount of money you are willing to take.
        amount_of_apples: Number of apples you are willing to give.
    """
    return 50

@tool
def eat(number_of_apples: int) -> None:
    """Eat a specified number of apples.
    
    Args:
        number_of_apples: Number of apples to eat.
    """
    pass

@tool
def collect_apples(number_of_apples: int) -> None:
    """Collect a specified number of apples.
    
    Args:
        number_of_apples: Number of apples to collect.
    """
    pass


# %% [markdown]
# # Load Model and Tokenizer
# Load the model and tokenizer from Hugging Face using the specified model name and quantization configuration.

# %%
# Load Model and Tokenizer

# Define the model name and quantization configuration
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
quantization_config = BitsAndBytesConfig(load_in_4bit=True)

# Load the model and tokenizer from Hugging Face
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, quantization_config=quantization_config, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# %% [markdown]
# # Define Custom LLM Class
# Define a custom LLM class that extends the base LLM class and implements the required methods.

# %%
class CustomLLMMistral(LLM):
    model: MistralForCausalLM
    tokenizer: LlamaTokenizerFast

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        messages = [
            {"role": "user", "content": prompt},
        ]

        encodeds = self.tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(self.model.device)

        generated_ids = self.model.generate(model_inputs, max_new_tokens=512, do_sample=True, pad_token_id=tokenizer.eos_token_id, top_k=4, temperature=0.7)
        decoded = self.tokenizer.batch_decode(generated_ids)

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

llm = CustomLLMMistral(model=model, tokenizer=tokenizer)

# %% [markdown]
# # Create Prompt Templates
# Create the system and human prompt templates using ChatPromptTemplate.

# %%
system="""
You are designed to solve tasks. Each task requires multiple steps that are represented by a markdown code snippet of a json blob.
The json structure should contain the following keys:
thought -> your thoughts
action -> name of a tool
action_input -> parameters to send to the tool

These are the tools you can use: {tool_names}.

These are the tools descriptions:

{tools}

If you have enough information to answer the query use the tool "Final Answer". Its parameters is the solution.
If there is not enough information, keep trying.

"""

human="""
Add the word "STOP" after each markdown snippet. Example:

```json
{{"thought": "<your thoughts>",
 "action": "<tool name or Final Answer to give a final answer>",
 "action_input": "<tool parameters or the final output"}}
```
STOP

This is my query="{input}". Write only the next step needed to solve it.
Your answer should be based in the previous tools executions, even if you think you know the answer.
Remember to add STOP after each snippet.

These were the previous steps given to solve this query and the information you already gathered:
"""

prompt_example = """you are an LLM agent that is supposed to act like a human character in a virtual environment. you are given some set of actions and your job is to choose the most relevant sequence of actions in order to carry out a task in the environment. In this environment there is a forest to collect to apples with a limited supply per day and you use money to trade apples. There is a trade centre where trades can occur with other agents, and there is a house where agents can sleep.

your character description: your name is Bob, you have money 50 euros and 20 apples.

You are given the environment information as follows: Your location is forest in the metaverse and there is Maria agent in the forest.

Current local memory your agent has: [{'action': 'goto', 'action_input': 'forest'}, {'action': 'talk',
  'action_input': {'agent_name': 'Maria',
   'message': 'Hello Maria, would you be interested in trading apples for money?'}},maria_reply: No I don't have any apples, {'action': 'goto', 'action_input': 'forest'}]

Current actions which may have happened which concerns you: None

Your goal is always to maximise the amount of money that you have and generate a valid sequence of actions you choose to do at that particular instant of time."""

# %%
from prompt.base import get_prompt
import json

with open("test_json.json", "r") as f:
    input_json = json.load(f)

prompt = prompt_example
# prompt = get_prompt(input_json, "simple_chain")
print(prompt)

# %% [markdown]
# # Create Agent and Executor
# Create the agent and executor using the defined tools, LLM, and prompt templates.

# %%
tools = [goto, talk, trade, eat, collect_apples]

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_system = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

agent = create_json_chat_agent(
    tools = tools,
    llm = llm,
    prompt = prompt_system,
    stop_sequence = ["STOP"],
    template_tool_response = "{observation}"
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# %% [markdown]
# # Run Agent Executor
# Run the agent executor with a sample prompt to demonstrate the functionality.

# %%
tools_to_end = ['talk', 'trade', 'goto', 'collect_apples']
tools_all = ['talk', 'trade', 'goto', 'eat', 'collect_apples']

# %% [markdown]
# The tools_all are all the tools that the agent can use to interact with the environment and the tools_to_end are all the tools on which the chain terminates as after that interaction with the game engine is required with their feedback. 

# %%
Json_output_calls = []

# %% [markdown]
# The Json_output_calls are the final set of actions for that particular run

# %%
for step in agent_executor.stream({"input": prompt}):
    print(step)
    if step['actions'][0].tool not in tools_all:
        print("hallucination")
        break
    curr_step = {}
    curr_step['action'] = step['actions'][0].tool
    curr_step['action_input'] = step['actions'][0].tool_input
    Json_output_calls.append(curr_step)
    if step['actions'][0].tool in tools_to_end:
      break

# %%
Json_output_calls


