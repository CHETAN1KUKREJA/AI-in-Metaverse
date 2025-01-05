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

    function_str = r"""
You can perform one of the following action:
1. go_to <location>: you can go to the nearby of a location if you are now \"outside\". You cannot go to outside, so choose exit for this case
2. enter <location>: you can enter a location if you are near to it
3. exit: you can exit the location you entered. Alias for \"go_to outside\"
3. take <amount> of <object>: you can pick some amount of objects if it exist in the vicinity
4. drop <amount> of <object>: you can drop some amount of objects from you
"""

    prompt = f"""
You are a helpful assistant. You are given with following information:

# world description
{get_world_prompt(world_dict)}

# vicinity description
{get_vicinity_prompt(vicinity_dict)}

# agent description
{get_agent_prompt(agent_dict)}

# contracts description
{get_contracts_prompt(contracts_list)}

# error description
{get_system_prompt(system_list)}

{function_str}

That's all the information you know for now. If you need information from other agents, you have to ask them. 

# rules
You should follow the rules:
0. assume is not allowed
1. get more money
2. be flexible, if you failed to do something, try something else
3. answer the other agent as much as possbile

Think step by step and output briefly your thought with 2 to 3 sentences. You must pay attention to the current state and vicinity. What you have done is also important, because you should not repeat meaningless. Finally output the action in a new line with the format \"Action: <action>\".
""".strip()

    return prompt
