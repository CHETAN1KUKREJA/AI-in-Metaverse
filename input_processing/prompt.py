from .prompt_sections.world import get_world_prompt
from .prompt_sections.vicinity import get_vicinity_prompt
from .prompt_sections.agent import get_agent_prompt
from .prompt_sections.contrast import get_contracts_prompt
from .prompt_sections.system import get_system_prompt

def get_prompt(input_json):
    world_dict = input_json["world"]
    vicinity_dict = input_json["vicinity"]
    agent_dict = input_json["agent"]
    contracts_list = input_json["contracts"]
    system_list = input_json["system"]

    description_prompt = f"""
You are an LLM agent that is supposed to act like a human character in a virtual environment. Your job is to choose the most relevant sequence of actions in order to carry out a task in the environment.

# world description
{get_world_prompt(world_dict)}

# vicinity description
{get_vicinity_prompt(vicinity_dict)}

# agent description
{get_agent_prompt(agent_dict)}

# contracts description
{get_contracts_prompt(contracts_list)}

# system description
{get_system_prompt(system_list)}

# end of description
That's all the information you know for now. If you need information from other agents, you have to ask them. You are not allowed to assume anything yourself.
""".strip()

    goal_prompt = f"""
# goal
Your goal is always to maximise the amount of money that you have.
""".strip()

    prompt = description_prompt + "\n\n" + goal_prompt + "\n\n"

    return prompt
