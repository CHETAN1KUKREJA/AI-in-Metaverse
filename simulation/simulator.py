from simulation.location import Location
from simulation.agent import Agent
from simulation.object import Object
from simulation.world import World

class Simulator:
    def __init__(self):
        self.market = Location("market", "trade objects with other agents", (10, 10))
        self.forest = Location("forest", "may exist fruits to pick", (-10, -10), objects=[Object("apple", 5, (1, 1))])
        self.outside = Location("outside", "go to locations such as market and forest")
        
        # alice = Agent("Alice", (8, 8), market, inventory={"apple": Object("apple", 3)}, available_actions=["take", "drop", "talk"])
        self.bob = Agent("Bob", (8, 8), self.outside, inventory={"money": Object("money", 10)}, available_actions=["go_to", "take", "drop", "talk", "enter", "exit"])
        self.outside.agents.append(self.bob)

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
            "world": self.world.world_description(self.bob),
            "vicinity": self.world.vicinity_description(self.bob),
            "agent": self.bob.agent_description(),
            "contracts": self.world.contracts_description(self.bob),
            "system": [],
            "actions": self.bob.action_description(),
        }
        
        return agent_input
    
    def update_state(self, action):
        target_agent = self.bob
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
                pass
            case "drop":
                pass
            case "enter":
                pass
            case "exit":
                pass
            case "play":
                pass
