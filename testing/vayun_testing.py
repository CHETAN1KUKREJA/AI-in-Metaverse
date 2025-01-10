# %%
# !pip install langchain
# !pip install accelerate
# !pip install -U bitsandbytes

# %%
from huggingface_hub import login

# Replace 'your_token_here' with your Hugging Face access token
token = "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"
token_sukhvansh = "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"
# Log in to Hugging Face Hub
login(token_sukhvansh)

print("Successfully logged in to Hugging Face Hub!")


# %%
from langchain.tools import BaseTool, StructuredTool, tool
import warnings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers.models.mistral.modeling_mistral import MistralForCausalLM
from transformers.models.llama.tokenization_llama_fast import LlamaTokenizerFast
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Mapping, Any


# %%
@tool
def goto(location: str) -> str:
    """go to places in the environment.
    
    args location: this can only take valid locations in the environment.

    """
    return "supermarket"

@tool
def talk(agent_name: str, message: str) -> str:
    """talk to another agent.

    args agent_name: Name of the agent you want to communicate to.
         message: the message you to communicate to the other agent. 
    """
    return "I am willing to trade 20 apples that is  a fair price as that is the current market price"

@tool
def trade(agent_name: str, amount_of_money: int, amount_of_apples: int) -> int:
    """trade to another agent.
    
    args agent_name: The name of the agent to which to trade with
         amount_of_money: amount of money you are willing to take
         amount_of_apples: number of apples willing to give 
    """
    return 50

@tool
def eat(number_of_apples:  int) -> None:
    """Use this function to eat
    
    args number_of_apples: number of apples to eat
    """


@tool
def collect_apples(number_of_apples:  int) -> None:
    """Use this function to collect apples
    
    
    args number_of_apples: number of apples to collect
    """

# %%
@tool
def goTo(location: str) -> str:
    """Go to a specific location in the environment.

    args location: The target location to go to. Must be a valid location in the environment.
    """
    return "Reached the location."

@tool
def take(object_name: str) -> str:
    """Take an object from the environment.

    args object_name: The name of the object to take. Must be present in the vicinity or location.
    """
    return "Object taken successfully."

@tool
def drop(object_name: str) -> str:
    """Drop an object in the environment.

    args object_name: The name of the object to drop. The object must be in the agent's inventory or hands.
    """
    return "Object dropped successfully."

@tool
def talk(volume: str, content: str) -> str:
    """Communicate with another agent.

    args volume: The volume at which to speak (e.g., "whisper", "normal", "shout").
         content: The message content to communicate.
    """
    return "Message communicated."

@tool
def message(to: str, content: str) -> str:
    """Send a message to an agent or a group of agents.

    args to: The target recipient(s) of the message. Can be "all", a group name, or a specific agent's name.
         content: The content of the message to send.
    """
    return "Message sent."

@tool
def enter(location: str) -> str:
    """Enter a specific location in the environment.

    args location: The name of the location to enter. Must be a valid and accessible location.
    """
    return "Entered the location."

@tool
def exit() -> str:
    """Exit the current location.

    args: None.
    """
    return "Exited the location."

@tool
def play(object_name: str) -> str:
    """Play with a specific object.

    args object_name: The name of the object to play with. The object must be present in the vicinity or the agent's inventory.
    """
    return "Played with the object."


# %%
tools = [goto, talk, trade, eat, collect_apples]

# %%
model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quantization_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, quantization_config=quantization_config, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

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

# %%
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

# %%
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# %%
from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

agent = create_json_chat_agent(
    tools = tools,
    llm = llm,
    prompt = prompt,
    stop_sequence = ["STOP"],
    template_tool_response = "{observation}"
)

# %%
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# %%
prompt = """you are an LLM agent that is supposed to act like a human character in a virtual environment. you are given some set of actions and your job is to choose the most relevant sequence of actions in order to carry out a task in the environment. In this environment there is a forest to collect to apples with a limited supply per day and you use money to trade apples. There is a trade centre where trades can occur with other agents, and there is a house where agents can sleep.

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

# %%
with open("test_json.json", "r") as f:
    input_json = json.load(f)

# %%
# prompt = get_prompt(input_json, "simple_chain")
# print(prompt)

# %%
# agent_executor.invoke({"input":prompt})

# %%
tools_to_end = ['talk', 'trade', 'goto', 'collect_apples']
tools_all = ['talk', 'trade', 'goto', 'eat', 'collect_apples']

# %%
Json_output_calls = []

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

# %%



