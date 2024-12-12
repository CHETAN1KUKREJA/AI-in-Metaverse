def get_world_prompt(input_json):

    #generated the detailed description of the world based on locations

    locations = input_json['locations']

    location_descriptions = []

    for location in locations:
        description = f"The location {location['name']} is one which can be used to {location['usage']} and is currently at a distance of {location['distance']} from you and you are {location['range']} it."
        location_descriptions.append(description)

    world_description = ' '.join(location_descriptions)

    return world_description

test_world_prompt = "You are given the environment information as follows: Your location coordinates are (10,20) in the metaverse and you are at the trade centre and there is an agent Maria at coordinates (11,20) also in the trade centre."