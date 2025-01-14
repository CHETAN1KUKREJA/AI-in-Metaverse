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
