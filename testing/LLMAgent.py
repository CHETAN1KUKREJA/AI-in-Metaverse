import json

class LLMAgent:
    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = []
        self.static_memory = ["basic_rules"]

    def make_decision(self, game_state_json):
        game_state = json.loads(game_state_json)
        prompt = self.create_prompt(game_state)
        decision = self.llm(prompt)
        self.update_memory(game_state, decision)
        return json.dumps(decision)

    def create_prompt(self, game_state):
        # Create a prompt based on the game state and memory
        prompt = f"Game state: {game_state}\n"
        prompt += f"Static memory: {self.static_memory}\n"
        prompt += f"Short-term memory: {self.short_term_memory}\n"
        return prompt

    def llm(self, prompt):
        # A very basic LLM simulation
        decision = {
            "action": "move",
            "direction": "north"
        }
        return decision

    def update_memory(self, game_state, decision):
        # Update short-term and long-term memory based on the game state and decision
        self.short_term_memory.append(game_state)
        if len(self.short_term_memory) > 5:
            self.long_term_memory.append(self.short_term_memory.pop(0))