from .prompt import get_prompt
from .actions import get_action_tools

def get_processed(input_json):
    return get_prompt(input_json), get_action_tools(input_json)

__all__ = ["get_processed"]