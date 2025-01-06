# LLM-Backend

## Environment Setup

Install the conda environment according to the `environment_setup.md`

## Prompt Engineering

### Example Prompt

TODO: This prompt is out of date. Need update

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

We provide the `single_step_planning.py` to test the prompt for a single step planning. You can test it on a local Qwen or Langchain with Mistral. Currently tested models are `Qwen [3B, 7B, 14B]` and `Mistral[7B]`.

Sample output:

```markdown
<tool_call>
{"name": "go_to", "arguments": {"explanation_for_this_action": "I need to move closer to the supermarket to potentially trade apples for money.", "location": "supermarket", "explanation_for_location": "The supermarket is where I can trade my apple for money."}}
</tool_call>
```

## Action Chaining

To test multi-step planning, a agent input state update is necessary. 

A very basic simulate tool is build for the agent input state. 

### Slot Filling Method

To reuse the pretrained target objective and decrease the output token as much as possible, a slot filling method is designed to let the LLM fill in the pattern like: "take <amount> of <object>". There is a pretrained objective for this blank filling so LLM should be very familar with it. In addition, this also reduce the output, since the json call structure (characters like ", {, } and sturctural key names) consumes lots of tokens.

`Qwen/Qwen2.5-14B-Instruct` and is used for testing planning. This is the most balanced conbination for now. Less powerful model will lead to a terriable planing and summaizing. More powerful model will cost more time. It uses ~32GB VRAM.

Usage:

```bash
export PYTHONPATH=/path/to/this/project/folder

# multi-round test
python tests/multi_step_planning.py

# single-round test
# test the planing part
python tests/single_step_planning.py
#test the summarization if slot filling method is used
python tests/single_step_summarizing.py
```

Here are a sample output. It's very reasonable and fast (average ~5s, worst ~10s, best ~3s)

```
############################################
Until now, I haven't performed any actions since the initial setup. My goal is to get more money, and the most straightforward way to do that would be to find a location where I can either earn or acquire money. Given my current inventory only contains money, and I'm outside with no objects around me, my best course of action is to head to the market if it were open, but since it's closed, I should consider going to the forest to gather fruits which could potentially be traded for money later.

Since the market is closed, I'll go to the forest to collect fruits.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 9.8745s
############################################
I am currently near the forest and my goal is to get more money. Since I am near the forest, I should enter it to potentially gather resources that I can later trade for money.

Action: enter forest
[{'name': 'enter', 'arguments': {'location': 'forest'}}]
Finished in 3.0587s
############################################
I am currently in the forest and I have 5 apples nearby that I can take. Since my goal is to get more money and apples can be traded for money, I should take the apples first.

Action: take 5 of apple
[{'name': 'take', 'arguments': {'amount': '5', 'objectName': 'apple'}}]
Finished in 3.3988s
############################################
I am currently in the forest and I have already picked 5 apples. Since I have 5 apples in my hand and I need more money, I could consider going to the market when it reopens. However, the market is closed now. For now, I don't see any other immediate action that would help me get more money directly from the forest. Therefore, I will exit the forest and check if anything changes or if there are other opportunities available.

Action: exit
[{'name': 'exit', 'arguments': {}}]
Finished in 6.5088s
############################################
I am currently outside and I have already picked 5 apples from the forest. Since I have enough apples for now and the market is closed, my next step should be to find another way to get more money or look for other resources. However, since there are no other options available right now, I will consider going back to the forest to check if there are any other useful items or if the market reopens.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 6.0410s
############################################
```

Some quantization of `Qwen/Qwen2.5-14B-Instruct` is also tested. `Qwen/Qwen2.5-14B-Instruct-AWQ` is a very good one, but it slightly faster than the original model but takes only ~12GB VRAM!

```
############################################
I am currently outside and my goal is to get more money. Since the market is closed and I don't have any items to trade, I should head to the forest to gather fruits that could potentially be traded later.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 6.4316s
############################################
I am near the forest and can pick fruits to trade later. Since I don't have any fruits yet, I should enter the forest to gather some.

Action: enter forest
[{'name': 'enter', 'arguments': {'location': 'forest'}}]
Finished in 4.0120s
############################################
I am currently in the forest and I have 5 apples nearby. Since I already have money, picking up the apples could be useful for trading later.

Action: take 5 of apple
[{'name': 'take', 'arguments': {'amount': '5', 'objectName': 'apple'}}]
Finished in 4.4323s
############################################
I have already picked 5 apples, which means I don't need to pick more right now. Since my goal is to get more money, I should consider going to the market when it reopens or look for other opportunities to earn money. However, since the market is closed, I will exit the forest and check if there are any other options available.

Action: exit
[{'name': 'exit', 'arguments': {}}]
Finished in 7.6802s
############################################
I have already picked 5 apples from the forest and am now back outside. Since I have enough apples for now, I should consider going to the market when it reopens to trade my apples for more money. For now, I will stay outside and look for other opportunities.

Action: wait
Traceback (most recent call last):
  File "/data/home/liujio/llm-backend/multi_step_planning.py", line 42, in <module>
    call_batch = llm.iterate_step([input_state])
  File "/data/home/liujio/llm-backend/backend/slot_filling/llm.py", line 37, in iterate_step
    self.update_memory(call_batch)
  File "/data/home/liujio/llm-backend/backend/slot_filling/llm.py", line 19, in update_memory
    match call["name"]:
TypeError: 'NoneType' object is not subscriptable
```

One disadvantage is that it's hallucinating a little bit with a chance. But if run it again, it works very well:

```
############################################
I am currently outside and my goal is to get more money. To achieve this, I should head to the forest to gather fruits, which I can later trade for money. My last action was none, so moving to the forest makes sense.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 6.8846s
############################################
I am near the forest and can pick fruits to potentially trade later. Since I don't have any fruits yet, I should enter the forest and start picking fruits.

Action: enter forest
[{'name': 'enter', 'arguments': {'location': 'forest'}}]
Finished in 4.1813s
############################################
I am currently in the forest and I have 5 apples nearby. Since I don't have any items in my inventory yet, I should take the apples. This will allow me to potentially trade them later for more money.

Action: take 5 of apple
[{'name': 'take', 'arguments': {'amount': '5', 'objectName': 'apple'}}]
Finished in 5.5992s
############################################
I have already picked 5 apples, and I have 10 units of money. Since I am in the forest and have already picked the available apples, I should consider going back outside to see if there are other opportunities to gather resources or find a way to increase my money.

Action: exit
[{'name': 'exit', 'arguments': {}}]
Finished in 6.3088s
############################################
I have already picked 5 apples from the forest and am now back outside. Since I already have apples, I should consider going to the market when it reopens to trade for more money. For now, I don't have any other options available.

Action: go_to market
[{'name': 'go_to', 'arguments': {'location': 'market'}}]
Finished in 5.9454s
############################################
```

### Langchain Method

TODO: Also test langchain Mistral here

## Socket Communication

To communication with the rendering and executing loop in Godot, a socket setup is build and used as the core loop in `main.py`.

To simulate the godot part, a testing client is provided in `tests/socket_communication.py`.

Usage:

```bash
export PYTHONPATH=/path/to/this/project/folder

# start client
python main.py

# test with testing client
python tests/socket_communication.py
```

Here is a sample output:

Client side:

```
{'world': {'datetime': '15.12.2024 10am', 'locations': [{'name': 'market', 'usage': "Trade objects with other agents. But it's closed now, currently there is no agents there. Reopen time is unknown.", 'distance': 2.8284271247461903, 'range': 'can_see'}, {'name': 'forest', 'usage': 'You can pick fruit in the forest. The fruit can be used trade.', 'distance': 25.45584412271571, 'range': 'can_see'}, {'name': 'outside', 'usage': 'go to locations', 'distance': 11.313708498984761, 'range': 'inside'}]}, 'vicinity': {'objects': [], 'agents': [], 'audio': []}, 'agent': {'name': 'George', 'health': 20, 'hunger': 3, 'happiness': 5, 'location': 'outside', 'currentAction': 'None', 'actionProgress': -1, 'age': 23, 'hands': [{'name': 'money', 'amount': 10}], 'inventory': [], 'ownership': []}, 'contracts': [], 'system': [], 'actions': [{'name': 'go_to', 'available': True}, {'name': 'talk', 'available': True}, {'name': 'take', 'available': True}, {'name': 'drop', 'available': True}, {'name': 'enter', 'available': True}, {'name': 'exit', 'available': True}, {'name': 'play', 'available': False}]}
Server response: [{'name': 'go_to', 'arguments': {'location': 'forest'}}]
```

Server side:

```
Server listening on localhost:33455
Connected to client at ('127.0.0.1', 37508)
Received: {'world': {'datetime': '15.12.2024 10am', 'locations': [{'name': 'market', 'usage': "Trade objects with other agents. But it's closed now, currently there is no agents there. Reopen time is unknown.", 'distance': 2.8284271247461903, 'range': 'can_see'}, {'name': 'forest', 'usage': 'You can pick fruit in the forest. The fruit can be used trade.', 'distance': 25.45584412271571, 'range': 'can_see'}, {'name': 'outside', 'usage': 'go to locations', 'distance': 11.313708498984761, 'range': 'inside'}]}, 'vicinity': {'objects': [], 'agents': [], 'audio': []}, 'agent': {'name': 'George', 'health': 20, 'hunger': 3, 'happiness': 5, 'location': 'outside', 'currentAction': 'None', 'actionProgress': -1, 'age': 23, 'hands': [{'name': 'money', 'amount': 10}], 'inventory': [], 'ownership': []}, 'contracts': [], 'system': [], 'actions': [{'name': 'go_to', 'available': True}, {'name': 'talk', 'available': True}, {'name': 'take', 'available': True}, {'name': 'drop', 'available': True}, {'name': 'enter', 'available': True}, {'name': 'exit', 'available': True}, {'name': 'play', 'available': False}]}
I am currently outside and my goal is to get more money. To achieve this, I should head to the forest to gather fruits which I can later trade for money. My current location does not provide any resources or opportunities to earn money.

Action: go_to forest
Finished in 6.8158s
Send: [{"name": "go_to", "arguments": {"location": "forest"}}]

Client disconnected
```
