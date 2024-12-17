# LLM-Backend

## Prompt Engineering

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

I build a very basic simulate tool for the agent input state. 

`Qwen/Qwen2.5-14B-Instruct` is used for planning and `Qwen/Qwen2.5-7B-Instruct` for summaizing. This is the most balanced conbination for now. Less powerful model will lead to a terriable planing and summaizing. More powerful model will cost more time.

Here are a sample output. 

```
############################################
Given my current situation, I have money but no items to trade. To increase my chances of getting more money, I should first gather some items that could be valuable for trading. The forest is a good place to start since I can pick fruit there.

Action: go_to forest
{'name': 'go_to', 'arguments': {'location': 'forest'}}
Finished in 7.9471s
############################################
Since I am currently outside and my hunger level is at 3, which could increase over time, it would be wise to first check if there are any resources nearby that I can use to satisfy my hunger or earn more money. Given that I am next to the forest where I can pick fruit, which might be useful for trading, I should head to the forest.

Action: enter forest
{'name': 'enter', 'arguments': {'location': 'forest'}}
Finished in 8.3216s
############################################
Since I am in the forest and I have the opportunity to pick apples which can be used for trading later, I should take the apples first.

Action: take 5 of apple
{'name': 'take', 'arguments': {'objectName': 'apple'}}
Finished in 4.6617s
############################################
Since I am in the forest and I have a low hunger level, I could pick some apples to eat or carry with me. However, since I already have 5 apples in my hand, picking more might not be necessary unless I plan to trade them later. Given that my main goal is to get more money, I should consider selling these apples once the market reopens.

Action: exit
{'name': 'exit', 'arguments': {}}
Finished in 8.0189s
############################################
```

## Change Logs

* 12.12.2024: Developed the prompt engineering parts with the prompt engineering subgroup members
* 13.12.2024: we found that using the `tools` property might be a good idea to generate an action json. Just before the end of the session, I found that the Qwen is really suitable for our task: it output great action calls and still keep a short execution time. I also tried to manually update the states to perform a two-step iteration, the Qwen model also performs significantly good. Based on these observations, I decided to use the Qwen 7B for now. It takes roughly 4~5 seconds to generate a single action call.
* 14.12.2024: I tried the model `NousResearch/Hermes-3-Llama-3.1-8B`. It's even faster (2~3 seconds) and still powerful. I also summarized the LLM stuffs into a backend class called `LLM`. Small update of the goal prompt to let the agent not ignore the talk around it even though it want to maximize its wealth.
* 16.12.2024: tried many models, finally decide to use `Qwen/Qwen2.5-14B-Instruct` for planning and `Qwen/Qwen2.5-7B-Instruct` for summaizing. The summarizing step can be performed manually though to further speed things up, but for now use LLM to summarize. Planning means to plan action within nature language and summarizing means to summarize the action into function call. 

