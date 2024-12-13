# LLM-Backend

## Prompt Engineering

During discussion on 13.12.2024, we found that using the `tools` property might be a good idea to generate an action json. Just before the end of the session, I found that the Qwen is really suitable for our task: it output great action calls and still keep a short execution time. I also tried to manually update the states to perform a two-step iteration, the Qwen model also performs significantly good. Based on these observations, I decided to use the Qwen 7B for now. It takes roughly 4~5 seconds to generate a single action call.

### Example Prompt

Here is an example prompt for Qwen from the `test_json.json`.

```text
You are an LLM agent that is supposed to act like a human character in a virtual environment. Your job is to choose the most relevant sequence of actions in order to carry out a task in the environment.

# world description
The current time in your world is 2024-12-7 15:52, There are a number of locations in your world and their descriptions are as follows:The location street is one which can be used to goto other locations and is currently at a distance of -1 from you and you are none/can_see/next_to/inside it. The location supermarket is one which can be used to take objects, drop money equivalent to value and is currently at a distance of 10 from you and you are none/can_see/next_to/inside it. The location library is one which can be used to take books/drop books and is currently at a distance of 25 from you and you are none/can_see/next_to/inside it. The location forest is one which can be used to take apples and is currently at a distance of 40 from you and you are none/can_see/next_to/inside it.

# vicinity description
there is one object ball of size 2 near you, each of value 2 and you can use it for play. you are not the owner. there is an agent <agentName> at a distance 10 to you. 
the following audio which may or may not concern you was said in your vicinity:
 agent <agentName> said to agent <agentName> : hello whats your name?.

# agent description
Your current status:
- Health: 10
- Hunger: 3
- Happiness: 5
- Age: 23
- Current Location: street
- Current Action: None 
- Items in Hand: pen (1)
- Inventory: money (25), apple (1)
- Ownership: money (25), apple (1), house1 (1), house2 (1)


# contracts description

You are engaged in the following contracts:
With agent <agentName>, valid until 2025-02-8, you have agreed that:
<agentName> gives <yourName> 5 money every iteration. <yourName> gives <agentName> 2 apples every iteration.

# system description
1. Another agent "Marie" was talking, and what you just said "Hello!" is covered. You may need to repeat it.
2. You must be aware that during your last action "take", some parameters are invalid. Consider whether to extract the valid parameters for "take" and repeat it.
3. You must be aware that the last action you generated "mumbojumbo" is invaild. You are not allowed to perform it.
4. You must be aware that the last action you generated "exit" is invaild. You are not allowed to perform it.
5. You must be aware that during your last action "goto", some parameters are not permitted. Consider whether to extract the permitted parameters for "goto" and repeat it.

# end of description
That's all the information you know for now. If you need information from other agents, you have to ask them. You are not allowed to assume anything yourself.

# goal
Your goal is always to maximise the amount of money that you have.
```

### Testing

We provide the `single_step_planning.py` to test the prompt for a single step planning. You can test it on a local Qwen. Currently tested models are `Qwen [3B, 7B, 14B]`.

Sample output:

```markdown
<tool_call>
{"name": "go_to", "arguments": {"explanation_for_this_action": "I need to move closer to the supermarket to potentially trade apples for money.", "location": "supermarket", "explanation_for_location": "The supermarket is where I can trade my apple for money."}}
</tool_call>
```

## Action Chaining

To test multi-step planning, a agent input state update is necessary. 

TODO: build a very basic update function for the agent input state.