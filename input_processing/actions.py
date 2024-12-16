import json


def go_to(
    location: str,
):
    """
    Go to a location from parameter. It can only be used when you are \"outside\". Use enter() to really enter the location.

    Args:
        location: The location to go to
    """


def take(
    analysis_state: str,
    explanation_for_this_action_and_arguments: str,
    objectName: str,
):
    """
    Take the object with the objectName parameter with you.

    Args:
        objectName: The name of the object to take with you
        analysis_state: You have to analysis your current state
        explanation_for_this_action_and_arguments: You have to explain why you choose this action and the corresponding arguments
    """
    
    
def drop(
    analysis_state: str,
    explanation_for_this_action_and_arguments: str,
    objectName: str,
):
    """
    Drop the object with the objectName parameter.

    Args:
        objectName: The name of the object to to drop
        analysis_state: You have to analysis your current state
        explanation_for_this_action_and_arguments: You have to explain why you choose this action and the corresponding arguments
    """


def talk(
    analysis_state: str,
    explanation_for_this_action_and_arguments: str,
    other_agent: str,
    message: str,
):
    """
    Talk with another angent. If you are asking questions, and need to hear the reply, you have to stop and wait.

    Args:
        other_agent: The acutal name of agent to talk to.
        message: the message to be talked.
        analysis_state: You have to analysis your current state
        explanation_for_this_action_and_arguments: You have to explain why you choose this action and the corresponding arguments
    """

def enter(
    location: str,
):
    """
    Enter a location from parameter if you are next to it.

    Args:
        location: The location to enter
    """

def exit(
    analysis_state: str,
    explanation_for_this_action_and_arguments: str,
):
    """
    Exit the location you just entered. Must be used after enter().

    Args:
        analysis_state: You have to analysis your current state
        explanation_for_this_action_and_arguments: You have to explain why you choose this action and the corresponding arguments
    """

def play(
    analysis_state: str,
    explanation_for_this_action_and_arguments: str,
    objectName: str,
):
    """
    Play the object with the objectName parameter.

    Args:
        objectName: The name of the object to to drop
        analysis_state: You have to analysis your current state
        explanation_for_this_action_and_arguments: You have to explain why you choose this action and the corresponding arguments
    """

tools = [go_to, take, drop, play, enter, exit, talk]


def get_action_tools(input_json):
    action_list = input_json["actions"]
    action_list = [
        action
        for action in action_list
        if "available" not in action or action["available"]
    ]
    available_list = []
    for action in action_list:
        entry = {}
        for k, v in action.items():
            if "available" not in k:
                entry[k] = v
        available_list.append(entry)
    action_tools = [eval(action["name"]) for action in available_list]

    return action_tools