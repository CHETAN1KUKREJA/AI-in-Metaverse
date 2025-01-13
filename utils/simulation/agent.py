class Agent:
    def __init__(
        self,
        name,
        pos,
        location,
        health=20,
        hunger=3,
        happiness=5,
        currentAction="None",
        actionProgress=-1,
        age=23,
        hands={},
        inventory={},
        ownership={},
        available_actions=[],
    ):
        self.name = name
        self.pos = pos
        self.health = health
        self.hunger = hunger
        self.happiness = happiness
        self.location = location
        self.currentAction = currentAction
        self.actionProgress = actionProgress
        self.age = age
        self.hands = hands
        self.inventory = inventory
        self.ownership = ownership
        self.all_actions = ["go_to", "talk", "take", "drop", "enter", "exit", "play"]
        self.available_actions = available_actions

    def agent_description(self):
        ret = {
            "name": self.name,
            "health": self.health,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "location": self.location.name,
            "currentAction": self.currentAction,
            "actionProgress": self.actionProgress,
            "age": self.age,
        }

        hand_list = []
        for object in self.hands.values():
            entry = {}
            entry["name"] = object.name
            entry["amount"] = object.amount
            hand_list.append(entry)
        ret["hands"] = hand_list

        inventory_list = []
        for object in self.inventory.values():
            entry = {}
            entry["name"] = object.name
            entry["amount"] = object.amount
            hand_list.append(entry)
        ret["inventory"] = inventory_list

        ownership_list = []
        for object in self.ownership.values():
            entry = {}
            entry["name"] = object.name
            entry["amount"] = object.amount
            hand_list.append(entry)
        ret["ownership"] = ownership_list

        return ret

    def action_description(self):
        ret = []
        for action in self.all_actions:
            entry = {}
            entry["name"] = action
            if action in self.available_actions:
                entry["available"] = True
            else:
                entry["available"] = False

            ret.append(entry)
        return ret
