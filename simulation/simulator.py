from simulation.location import Location
from simulation.agent import Agent
from simulation.object import Object
from simulation.world import World


class Simulator:
    def __init__(self):
        self.market = Location(
            "market", "Trade objects with other agents. But it's closed now, currently there is no agents there. Reopen time is unknown.", (10, 10)
        )
        self.forest = Location(
            "forest",
            "You can pick fruit in the forest. The fruit can be used trade.",
            (-10, -10),
            objects={"apple": Object("apple", 5, 1, "take or drop", (1, 1))},
        )
        self.outside = Location("outside", "go to locations")

        # alice = Agent("Alice", (8, 8), market, inventory={"apple": Object("apple", 3)}, available_actions=["take", "drop", "talk"])
        self.agent = Agent(
            "George",
            (8, 8),
            self.outside,
            inventory={"money": Object("money", 10, 0.1, "take or drop")},
            available_actions=["go_to", "take", "drop", "talk", "enter", "exit"],
        )
        self.outside.agents[self.agent.name] = self.agent

        self.world = World(
            "15.12.2024 10am",
            {
                "market": self.market,
                "forest": self.forest,
                "outside": self.outside,
            },
        )

    def get_agent_input_state(self):
        agent_input = {
            "world": self.world.world_description(self.agent),
            "vicinity": self.world.vicinity_description(self.agent),
            "agent": self.agent.agent_description(),
            "contracts": self.world.contracts_description(self.agent),
            "system": [],
            "actions": self.agent.action_description(),
        }

        return agent_input

    def update_state(self, action):
        target_agent = self.agent
        match action["name"]:
            case "go_to":
                assert target_agent.location == self.outside

                assert "arguments" in action
                assert "location" in action["arguments"]
                assert action["arguments"]["location"] in self.world.locations.keys()

                target_agent.pos = self.world.locations[action["arguments"]["location"]].pos
            case "talk":
                pass
            case "take":
                name = action["arguments"]["objectName"]
                target_agent.inventory[name] = target_agent.location.objects[name]
                target_agent.location.objects.pop(name)
            case "drop":
                pass
            case "enter":
                assert target_agent.location == self.outside

                assert "arguments" in action
                assert "location" in action["arguments"]
                assert action["arguments"]["location"] in self.world.locations.keys()

                target_agent.location = self.world.locations[action["arguments"]["location"]]
            case "exit":
                target_agent.location = self.world.locations["outside"]
            case "play":
                pass
