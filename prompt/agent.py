def get_agent_prompt(agent):
    # Generate a detailed description for the agent's attributes.
    
    if not agent:
        return "No agent data available."

    items_in_hand = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['hands']])
    inventory = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['inventory']])
    ownership = ', '.join([f"{item['name']} ({item['amount']})" for item in agent['ownership']])

    agent_description = (
        f"\nYour current status:\n"
        f"- Health: {agent['health']}\n"
        f"- Hunger: {agent['hunger']}\n"
        f"- Happiness: {agent['happiness']}\n"
        f"- Age: {agent['age']}\n"
        f"- Current Location: {agent['location']}\n"
        f"- Current Action: {agent['currentAction']} "
        f"({agent['actionProgress']}% completed)\n"
        f"- Items in Hand: {items_in_hand}\n"
        f"- Inventory: {inventory}\n"
        f"- Ownership: {ownership}"
    )
    return agent_description
