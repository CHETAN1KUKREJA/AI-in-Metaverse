import math

def get_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


class World:
    def __init__(self, datetime, locations={}):
        self.datatime = datetime
        self.locations = locations

    def world_description(self, target_agent):
        ret = {"datetime": self.datatime, "locations": []}
        for location in self.locations.values():
            entry = {}
            entry["name"] = location.name
            entry["usage"] = location.usage

            if target_agent.location == self.locations["outside"]:
                distance = get_distance(target_agent.pos, location.pos)
            else:
                distance = -1
            entry["distance"] = distance

            if target_agent.location == location:
                range = "inside"
            elif target_agent.location == self.locations["outside"]:
                if distance >= 1:
                    range = "can_see"
                else:
                    range = "next_to"
            else:
                range = "none"
            entry["range"] = range

            ret["locations"].append(entry)

        return ret

    def vicinity_description(self, target_agent):
        location = target_agent.location
        object_list, agent_list, audio_list = [], [], []
        for object in location.objects:
            if get_distance(object.pos, target_agent.pos) < 3:
                entry = {}
                entry["name"] = object.name
                entry["amount"] = object.amount
                object_list.append(entry)
                
        for agent in location.agents:
            if target_agent.name == agent.name:
                continue
            if get_distance(agent.pos, target_agent.pos) < 3:
                entry = {}
                entry["name"] = agent.name
                entry["distance"] = get_distance(agent.pos, target_agent.pos)
                agent_list.append(entry)
                
        for audio in location.audios:
            if get_distance(audio.agent_from.pos, target_agent.pos) < 3:
                entry = {}
                entry["from"] = audio.agent_from.name
                entry["content"] = audio.content
                audio_list.append(entry)
                
        return {"objects": object_list, "agents": agent_list, "audio": audio_list}
            
    def contracts_description(self, target_agent):
        return []