def get_vicinity_prompt(vicinity):

    # Generate a detailed description of the vicinity based on objects, agents, and audio.

    description_parts = []

    if len(vicinity["objects"]) > 0:
        object_descriptions = []
        for obj in vicinity["objects"]:
            amount_str = "one" if obj["amount"] == 1 else str(obj["amount"])
            # ownership_str = "are the owner" if obj["owner"] == True else "are not the owner"
            object_desc = (
                f"there {('is' if obj['amount'] == 1 else 'are')} {amount_str} "
                f"object {obj['name']} near you, "
                f"you can use it for {obj['usage']}. "
                # f"you {ownership_str}."
            )
            object_descriptions.append(object_desc)
        object_description = " ".join(object_descriptions)
    else:
        object_description = "There is no object around you!"

    if len(vicinity["agents"]) > 0:
        agent_descriptions = []
        for agent in vicinity["agents"]:
            agent_desc = f"there is an agent {agent['name']} at a distance {agent['distance']} to you."
            agent_descriptions.append(agent_desc)
        agent_description = " ".join(agent_descriptions)
    else:
        agent_description = "There is no other agent here!"

    if len(vicinity["audio"]) > 0:
        audio_descriptions = ["\nthe following audio which may or may not concern you was said in your vicinity:\n"]
        for audio in vicinity["audio"]:
            audio_desc = f"agent {audio['from']} said to agent {audio['to']} : {audio['content']}."
            audio_descriptions.append(audio_desc)
        audio_description = " ".join(audio_descriptions)
    else:
        audio_description = "There is no talk in your vicinity."

    return object_description + "\n\n" + agent_description + "\n\n" + audio_description + "\n\n"
