from .prompt_slot_filling import get_prompt
from .actions import tools

#TODO:Check if this is needed
# def get_processed(input_json):
#     return get_prompt(input_json), get_action_tools(input_json)


__all__ = ["get_prompt", "tools"]
