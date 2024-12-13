def get_vicinity_prompt(vicinity):

    #Generate a detailed description of the vicinity based on objects, agents, and audio.

    description_parts = []

    if 'objects' in vicinity:
        object_descriptions = []
        for obj in vicinity['objects']:
            amount_str = "one" if obj['amount'] == 1 else str(obj['amount'])
            ownership_str = "are the owner" if obj['owner'] == True else "are not the owner"
            object_desc = (f"there {('is' if obj['amount'] == 1 else 'are')} {amount_str} "
                           f"object {obj['name']} of size {obj['size']} near you, "
                           f"each of value {obj['value']} and you can use it for {obj['usage']}. "
                           f"you {ownership_str}.")
            object_descriptions.append(object_desc)
        description_parts.extend(object_descriptions)

    if 'agents' in vicinity:
        agent_descriptions = []
        for agent in vicinity['agents']:
            agent_desc = f"there is an agent {agent['name']} at a distance {agent['distance']} to you."
            agent_descriptions.append(agent_desc)
        description_parts.extend(agent_descriptions)

    if 'audio' in vicinity:
        audio_descriptions = ["\nthe following audio which may or may not concern you was said in your vicinity:\n"]
        for audio in vicinity['audio']:
            audio_desc = f"agent {audio['from']} said to agent {audio['to']} : {audio['content']}."
            audio_descriptions.append(audio_desc)
        description_parts.extend(audio_descriptions)

    return " ".join(description_parts)

test_vicinity_prompt = ""