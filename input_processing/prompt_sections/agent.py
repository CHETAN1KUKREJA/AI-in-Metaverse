def get_agent_prompt(agent):
    # Generate a detailed description for the agent's attributes.
    
    if not agent:
        return "No agent data available."

    items_in_hand = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['hands']])
    inventory = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['inventory']])
    ownership = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['ownership']])

    agent_description = ""
    agent_description += "Your current status:\n"
    agent_description += f"- Name: {agent['name']}\n"
    agent_description += f"- Health: {agent['health']}\n"
    agent_description += f"- Hunger: {agent['hunger']}\n"
    agent_description += f"- Happiness: {agent['happiness']}\n"
    agent_description += f"- Age: {agent['age']}\n"
    agent_description += f"- Current Location: {agent['location']}\n"
    progress_str = "" if agent['actionProgress'] == "-1" else f"({agent['actionProgress']}% completed)"
    agent_description += f"- Current Action: {agent['currentAction']} {progress_str}\n"
    agent_description += f"- Items in Hand: {items_in_hand}\n"
    agent_description += f"- Inventory: {inventory}\n"
    agent_description += f"- Ownership: {ownership}\n"

    return agent_description
