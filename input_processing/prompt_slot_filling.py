from .prompt_sections.world import get_world_prompt
from .prompt_sections.vicinity import get_vicinity_prompt
from .prompt_sections.agent import get_agent_prompt
from .prompt_sections.contrast import get_contracts_prompt
from .prompt_sections.system import get_system_prompt


def get_prompt(input_json, multi_step=False):
    world_dict = input_json["world"]
    vicinity_dict = input_json["vicinity"]
    agent_dict = input_json["agent"]
    contracts_list = input_json["contracts"]
    system_list = input_json["system"]

    function_str_single = r"""
You can perform one of the following action:
1. go_to <location>: you can go to the nearby of a location if you are now \"outside\". You cannot go to outside, so choose exit for this case
2. enter <location>: you can enter a location if you are near to it
3. exit: you can exit the location you entered. Alias for \"go_to outside\"
3. take <amount> of <object>: you can pick some amount of objects if it exist in the vicinity
4. drop <amount> of <object>: you can drop some amount of objects from you
5. talk to <agent> with \"<content>\": you can talk to an nearby agent with the content. Content should be as daily talk. The agent must exist.
""".strip()

    function_str_multi = r"""
You can choose within following action patterns:
1. go_to <location>: you can go to the nearby of a location only if you are now \"outside\". You cannot go to outside, so choose \"exit\" for this case
2. enter <location>: you can enter a location if you are near to it
3. exit: you can exit the location you entered. Alias for \"go_to outside\"
3. take <amount> of <object>: you can pick some amount of objects if it exist in the vicinity
4. drop <amount> of <object>: you can drop some amount of objects from you
5. talk to <agent> with \"<content>\": you can talk to an nearby agent with the content. Content should be as daily talk. The agent must exist.
""".strip()

    target_single = """
Think step by step and output briefly your thought with 2 to 3 sentences. Pay attention to the restriction of the actions when choosing. You must pay attention to the current state and vicinity. What you have done is also important, because you should not repeat meaningless. Finally output the action in a new line with the format \"Action: <action>\".    
"""
    
    target_multi = """
You should plan a list of actions. You must pay attention to the pattern and restriction of the actions when choosing. You must also pay attention to the current state and vicinity. What you have done is also important, because you should not repeat meaningless. Think step by step and output briefly your thought with several sentences. Finally output the list of actions in a new line with the format: \"Action: <action_1>, <action_2>, ..., <action_x>\".
""".strip()

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

{function_str_multi if multi_step else function_str_single}

That's all the information you know for now. If you need information from other agents, you have to ask them. 

# rules
You should follow the rules:
0. assume is not allowed
1. get more money
2. be flexible, if you failed to do something, try something else
3. answer the other agent as much as possbile

{target_multi if multi_step else target_single}
""".strip()

    return prompt
