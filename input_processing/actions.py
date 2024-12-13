import json


def go_to(
    explanation_for_this_action: str,
    location: str,
    explanation_for_location: str,
):
    """
    Go to a location from parameter, but not enter it.

    Args:
        location: The location to go to
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_location: You have to explain briefly why you choose this location
    Returns:
        No return
    """


def take(
    explanation_for_this_action: str,
    objectName: str,
    explanation_for_object_name: str,
):
    """
    Take the object with the objectName parameter with you.

    Args:
        objectName: The name of the object to take with you
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_object_name: You have to explain briefly why you choose this object name
    Returns:
        No return
    """
    
    
def drop(
    explanation_for_this_action: str,
    objectName: str,
    explanation_for_object_name: str,
):
    """
    Drop the object with the objectName parameter.

    Args:
        objectName: The name of the object to to drop
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_object_name: You have to explain briefly why you choose this object name
    Returns:
        No return
    """


def talk(
    explanation_for_this_action: str,
    other_agent: str,
    explanation_for_other_agent: str,
    message: str,
    explanation_for_message: str,
):
    """
    Talk with another angent. If you are asking questions, and need to hear the reply, you have to stop and wait.

    Args:
        other_agent: The acutal name of agent to talk to.
        message: the message to be talked.
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_other_agent: You have to explain briefly why you choose to talk to this agent
        explanation_for_message: You have to explain briefly how you generate the message
    Returns:
        No return
    """

def enter(
    explanation_for_this_action: str,
    location: str,
    explanation_for_location: str,
):
    """
    Enter a location from parameter.

    Args:
        location: The location to go to
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_location: You have to explain briefly why you choose this location
    Returns:
        No return
    """

def exit(
    explanation_for_this_action: str,
):
    """
    Exit the location you just entered. Must be used after enter().

    Args:
        explanation_for_this_action: You have to explain briefly why you choose this action
    Returns:
        No return
    """

def play(
    explanation_for_this_action: str,
    objectName: str,
    explanation_for_object_name: str,
):
    """
    Play the object with the objectName parameter.

    Args:
        objectName: The name of the object to to drop
        explanation_for_this_action: You have to explain briefly why you choose this action
        explanation_for_object_name: You have to explain briefly why you choose this object name
    Returns:
        No return
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