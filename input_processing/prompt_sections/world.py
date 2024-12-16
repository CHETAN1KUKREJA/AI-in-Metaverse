def get_world_prompt(input_json):

    # generated the detailed description of the world based on locations

    locations = input_json["locations"]

    # location_descriptions = []

    # for location in locations:
    #     description = f"The location \"{location['name']}\" is one which can be used to {location['usage']} and is currently at a distance of {location['distance']} from you and you are {location['range']} it."
    #     location_descriptions.append(description)

    # world_description = " ".join(location_descriptions)

    # world_description = (
    #     f"The current time in your world is {input_json['datetime']}, There are a number of locations in your world and their descriptions are as follows:"
    #     + world_description
    # )
    
    ret = f"The current time in your world is {input_json['datetime']}, There are a number of locations in your world:\n"
    for idx, location in enumerate(locations):
        ret += f"{idx+1}: {location['name']}\n"
        ret += f"- Usage: {location['usage']}\n"
        
        match location['range']:
            case "next_to":
                ret += f"- You are next to it."
            case "can_see":
                ret += f"- You can see it. It {location['distance']:.1f} away from you."
            case "inside":
                ret += f"- You are currently inside it."
        ret += "\n"
    return ret