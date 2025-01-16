def go_to(
        location: str,
):
    """
    Go to a location.

    Args:
        location: The location to go to
    """


def take(
        objectName: str,
):
    """
    Take the object.

    Args:
        objectName: The name of the object to take with you
    """


def drop(
        objectName: str,
):
    """
    Drop the object.

    Args:
        objectName: The name of the object to to drop
    """


def talk(
        other_agent: str,
        message: str,
):
    """
    Talk with existing angent. The agent must appears in the information given. If you are asking questions, and need to hear the reply, you have to stop and wait.

    Args:
        other_agent: The name of agent to talk to. The agent must exist.
        message: the message to be talked.
    """


def enter(
        location: str,
):
    """
    Enter a location.
    
    Args:
        location: The location to enter
    """


def exit(
):
    """
    exit the location.
    """


def play(
        objectName: str,
):
    """
    Play the object.

    Args:
        objectName: The name of the object to to drop
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
