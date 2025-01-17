# LLM-Backend

## Environment Setup

Install the conda environment according to the `environment_setup.md`

## Project Structure

- /resources - Folder for not-code files
- /src - Folder for all main project-related code files
  - /src/llm - Folder for request-processing code
  - /src/promts - Folder for promt-generation code
  - /src/sockets - Folder for socket-connectivity code
- /utils - Folder for additional testing/simulating/etc. of main project-related code


## Prompt Engineering (Some stuff may be deprecated)

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

We provide the `single_step_planning.py` to test the prompt for a single step planning. You can test it on a local Qwen or Langchain with Mistral. Currently tested models are `Qwen [3B, 7B, 14B]` and `Mistral[7B]` with langchain.

Sample output:

```markdown
<tool_call>
{"name": "go_to", "arguments": {"location": "supermarket"}}
</tool_call>
```

## Action Chaining

To test multi-step planning, a agent input state update is necessary. 

A very basic simulate tool is build for the agent input state. 

### Slot Filling Method

To reuse the pretrained target objective and decrease the output token as much as possible, a slot filling method is designed to let the LLM fill in the pattern like: "take \<amount\> of \<object\>". There is a pretrained objective for this blank filling so LLM should be very familar with it. In addition, this also reduce the output, since the json call structure (characters like ", {, } and sturctural key names) consumes lots of tokens.

`Qwen/Qwen2.5-14B-Instruct` and is used for testing planning. This is the most balanced conbination for now. Less powerful model will lead to a terriable planing and summaizing. More powerful model will cost more time. It uses \~32GB VRAM.

Usage:

```bash
export PYTHONPATH=/path/to/this/project/folder

# multi-round test
python tests/multi_step_planning.py

# single-round test
# test the planing part
python tests/single_step_planning.py
# test the summarization if slot filling method is used
python tests/single_step_summarizing.py
```

Here are a sample output. It's very reasonable and fast (average \~5s, worst \~10s, best \~3s)

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

Some quantization of `Qwen/Qwen2.5-14B-Instruct` is also tested. `Qwen/Qwen2.5-14B-Instruct-AWQ` is a very good one, because it slightly faster than the original model but takes only \~12GB VRAM! The average runtime is only 3\~4s!

```
############################################
I am currently outside and my goal is to get more money. Since the market is closed and I don't have any items to trade right now, I should head to the forest to gather fruits which could be valuable for trading later.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 4.3896s
############################################
I am near the forest and can pick fruits to potentially earn more money. Since I don't have any fruits yet, I should enter the forest to start picking.

Action: enter forest
[{'name': 'enter', 'arguments': {'location': 'forest'}}]
Finished in 3.1312s
############################################
I am currently in the forest and I have 5 apples nearby. Since I already have money, picking up the apples could be useful for trading later. 

Action: take 5 of apple
[{'name': 'take', 'arguments': {'amount': '5', 'objectName': 'apple'}}]
Finished in 3.3090s
############################################
I have already picked 5 apples, and I have 10 units of money. Since I am in the forest and have already picked the available apples, I should consider going back outside or to another location like the market when it reopens. For now, I will exit the forest.

Action: exit
[{'name': 'exit', 'arguments': {}}]
Finished in 4.7610s
############################################
I have already picked 5 apples from the forest and am now back outside. Since I have enough apples for now, I should consider going to the market when it reopens to trade my apples for more money. For now, I don't have any immediate action to take since the market is closed.

Action: None
Traceback (most recent call last):
  File "/home/student1/llm-backend/tests/multi_step_planning.py", line 43, in <module>
    call_batch = llm.iterate_step([input_state])
  File "/home/student1/llm-backend/backend/slot_filling/llm.py", line 37, in iterate_step
    self.update_memory(call_batch)
  File "/home/student1/llm-backend/backend/slot_filling/llm.py", line 19, in update_memory
    match call["name"]:
TypeError: 'NoneType' object is not subscriptable
```

One disadvantage is that it's hallucinating a little bit with a chance. But if run it again, it works very well:

```
############################################
I am currently outside and my goal is to get more money. Since the market is closed and I don't have any items to trade, I should head to the forest to gather fruits which could be valuable for trading when the market reopens.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 4.4199s
############################################
I am near the forest and can pick fruits to potentially trade for more money later. Since I don't have any fruits yet, I should enter the forest to start picking.

Action: enter forest
[{'name': 'enter', 'arguments': {'location': 'forest'}}]
Finished in 3.2208s
############################################
I am currently in the forest and I have 5 apples nearby. Since I already have money, picking up the apples could be useful for trading later. 

Action: take 5 of apple
[{'name': 'take', 'arguments': {'amount': '5', 'objectName': 'apple'}}]
Finished in 3.2725s
############################################
I have already picked 5 apples from the forest, and I currently have 10 money. Since I am at the maximum capacity for apples, I should consider exiting the forest to either trade or find another resource.

Action: exit
[{'name': 'exit', 'arguments': {}}]
Finished in 3.7640s
############################################
I have already picked 5 apples from the forest and am back outside. Since I already have apples and am not near any other source of items or locations where I can trade, I should consider going to the market when it reopens to potentially earn more money.

However, since the market is currently closed, my best option might be to return to the forest to gather more apples for trading later.

Action: go_to forest
[{'name': 'go_to', 'arguments': {'location': 'forest'}}]
Finished in 6.1117s
############################################
```

#### Update: Multi-step planning

In the meeting with Puxuan, I found that the godot team expect a list of actions instead of a single one. So I also tried on that. Here are some of the result: 

Result 1: The LLM planed in a very long period, but is hallucinating because it doesn't know the things in the future, such as the "take 5 of fruit".

```
############################################
Currently, I am located outside with 10 units of money. My goal is to acquire more money. To achieve this, I could potentially gather fruits from the forest and then trade them at the market once it reopens. However, since the market is closed and there are no other agents or objects nearby, my immediate action should be to head towards the forest to collect fruits.

Action: go_to forest, enter forest, take 5 of fruit, exit, go_to market
[[{'name': 'go_to', 'arguments': {'location': 'forest'}}, {'name': 'enter', 'arguments': {'location': 'forest'}}, {'name': 'take', 'arguments': {'amount': '5', 'objectName': 'fruit'}}, {'name': 'exit', 'arguments': {}}, {'name': 'go_to', 'arguments': {'location': 'market'}}]]
############################################
```

Result 2: The problem is result 1 appears again: "take 10 fruit". It has additionally logical mistake, such as: "Action: go_to market, enter forest".

```
############################################
I am currently outside and my goal is to get more money. To achieve this, I should first head to the forest to gather fruits which can potentially be traded for money later on at the market. Since the market is closed, going to the forest makes sense.

Action: go_to forest, enter forest, take 10 fruit, exit, go_to market, enter market
[[{'name': 'go_to', 'arguments': {'location': 'forest'}}, {'name': 'enter', 'arguments': {'location': 'forest'}}]]
Finished in 6.0420s
############################################
I am currently in the forest and I have 5 apples nearby. Since I don't have any apples in my inventory yet, I should take some apples. After that, I can consider exiting the forest to find another location where I might be able to trade or earn more money.

Action: take 2 of apple, exit
[[{'name': 'take', 'arguments': {'amount': '2', 'objectName': 'apple'}}, {'name': 'exit', 'arguments': {}}]]
Finished in 5.1394s
############################################
I have already picked apples from the forest and am now back outside. Since I have apples and money, I could consider going to the market once it reopens to see if I can trade or buy more items. However, since the market is closed, I should look for another opportunity to increase my resources or explore further.

Action: go_to market, enter forest
[[{'name': 'go_to', 'arguments': {'location': 'market'}}, {'name': 'enter', 'arguments': {'location': 'forest'}}]]
Finished in 5.5919s
############################################
```

As summary, multi-step planning is taking more time for planning additional steps as well as sacrificing some performance (intelligence), since the confident interval decrease exponentially. Also, if the state of an agent changes during executing and LLM need to re-plan, the rest of the commands is wasted as well as the time for planning them. I would recommand to use the single step planning. Noe the single step planning returns a list of a single call. This should fulfills the requirement of the godot team.

#### Update: Further speed up using vllm

The LLM processing is further speed up! It now only consume 1.4~1.9s to generate the output without lossing quality. An example output would be:

```
############################################
Processed prompts: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:01<00:00,  1.89s/it, est. speed input: 303.91 toks/s, output: 35.41 toks/s]
([[{'name': 'go_to', 'arguments': {'location': 'forest'}}]], ['I am currently located outside with 10 units of money. My goal is to gather more resources or find opportunities to increase my money. Since the market is closed and there are no objects or agents nearby, I should head to the forest to potentially gather fruits which could be valuable for trading later on.\n\nAction: go_to forest'])
Finished in 1.8997s
############################################
```

But it will consume ALL the VRAM for caching KV pairs. That's the reason that it can speed things up so much.

### Langchain Method

We also tried Langchain framework with inner LLM `Mistral-7B-Instruct`. It is not as intelligent as the above `Qwen2.5-14B-Instruct`, so it's halllucinating most of the time. Also it's even slower than `Qwen2.5-14B-Instruct`. Here is some sample outputs:

```
{'actions': [AgentAction(tool='talk', tool_input={'agent_name': 'George', 'message': 'I would like to know if the market is open and if there are any agents there.'}, log='```json\n{"thought": "The \'market\' location is currently closed and there are no agents there. The \'forest\' location is where I can pick fruit to trade. I can go to \'outside\' from my current location. I have 10 units of money and can trade using my \'money\' hand. I need to eat to increase my health and happiness. I can collect apples to add to my inventory.",\n "action": "talk",\n "action_input": {\n    "agent_name": "George",\n    "message": "I would like to know if the market is open and if there are any agents there."\n  }\n}```')], 'messages': [AIMessage(content='```json\n{"thought": "The \'market\' location is currently closed and there are no agents there. The \'forest\' location is where I can pick fruit to trade. I can go to \'outside\' from my current location. I have 10 units of money and can trade using my \'money\' hand. I need to eat to increase my health and happiness. I can collect apples to add to my inventory.",\n "action": "talk",\n "action_input": {\n    "agent_name": "George",\n    "message": "I would like to know if the market is open and if there are any agents there."\n  }\n}```', additional_kwargs={}, response_metadata={})]}
[{'action': 'talk', 'action_input': {'agent_name': 'George', 'message': 'I would like to know if the market is open and if there are any agents there.'}}]
Finished in 11.2823s

{'actions': [AgentAction(tool='talk', tool_input={'agent_name': 'George', 'message': "I'd like to know if the market is open or when it will reopen."}, log='```json\n{"thought": "The query contains information about various locations, the user\'s current location, and the user\'s current state. The \'market\' location is currently closed and no agents are present. The \'forest\' location is at a greater distance but can be seen and fruit can be picked and used for trade. The user\'s current location is \'outside\'. The user\'s hunger level is 3 and they have 10 units of money.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "I\'d like to know if the market is open or when it will reopen."\n }\n}```')], 'messages': [AIMessage(content='```json\n{"thought": "The query contains information about various locations, the user\'s current location, and the user\'s current state. The \'market\' location is currently closed and no agents are present. The \'forest\' location is at a greater distance but can be seen and fruit can be picked and used for trade. The user\'s current location is \'outside\'. The user\'s hunger level is 3 and they have 10 units of money.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "I\'d like to know if the market is open or when it will reopen."\n }\n}```', additional_kwargs={}, response_metadata={})]}
[{'action': 'talk', 'action_input': {'agent_name': 'George', 'message': "I'd like to know if the market is open or when it will reopen."}}]
Finished in 6.2222s

{'actions': [AgentAction(tool='goto', tool_input={'location': 'market', 'speed': 1}, log='```json\n{"thought": "The query contains information about locations, the current agent\'s position, and the available actions. I will first try to go to the market to check if it\'s open and if there are any agents there. If not, I will go to the forest to pick some fruit and trade with other agents.",\n "action": "goto",\n "action_input": {"location": "market", "speed": 1}}```')], 'messages': [AIMessage(content='```json\n{"thought": "The query contains information about locations, the current agent\'s position, and the available actions. I will first try to go to the market to check if it\'s open and if there are any agents there. If not, I will go to the forest to pick some fruit and trade with other agents.",\n "action": "goto",\n "action_input": {"location": "market", "speed": 1}}```', additional_kwargs={}, response_metadata={})]}
[{'action': 'goto', 'action_input': {'location': 'market', 'speed': 1}}]
Finished in 4.4067s

{'actions': [AgentAction(tool='talk', tool_input={'agent_name': 'George', 'message': "I'd like to know the current status of the market and the forest."}, log='```json\n{"thought": "The market location is currently closed and there are no agents there. The forest location is a place where fruit can be picked and used for trade. I am currently located outside, with a distance of 11.313708498984761 units from the market and 25.45584412271571 units from the forest.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "I\'d like to know the current status of the market and the forest."\n }\n}```')], 'messages': [AIMessage(content='```json\n{"thought": "The market location is currently closed and there are no agents there. The forest location is a place where fruit can be picked and used for trade. I am currently located outside, with a distance of 11.313708498984761 units from the market and 25.45584412271571 units from the forest.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "I\'d like to know the current status of the market and the forest."\n }\n}```', additional_kwargs={}, response_metadata={})]}
[{'action': 'talk', 'action_input': {'agent_name': 'George', 'message': "I'd like to know the current status of the market and the forest."}}]
Finished in 8.2450s

{'actions': [AgentAction(tool='talk', tool_input={'agent_name': 'George', 'message': "Let's go to the forest and collect some apples to trade with other agents at the market when it opens."}, log='```json\n{"thought": "The query provides the current location of the agent \'George\' as \'outside\'. The query also lists available locations with their names, distances, usages, and ranges. The market location is currently closed and the forest location has fruit that can be used for trade. The agent\'s health, hunger, and happiness levels are also provided. No tools or actions have been executed yet.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "Let\'s go to the forest and collect some apples to trade with other agents at the market when it opens."\n }\n}```')], 'messages': [AIMessage(content='```json\n{"thought": "The query provides the current location of the agent \'George\' as \'outside\'. The query also lists available locations with their names, distances, usages, and ranges. The market location is currently closed and the forest location has fruit that can be used for trade. The agent\'s health, hunger, and happiness levels are also provided. No tools or actions have been executed yet.",\n "action": "talk",\n "action_input": {\n   "agent_name": "George",\n   "message": "Let\'s go to the forest and collect some apples to trade with other agents at the market when it opens."\n }\n}```', additional_kwargs={}, response_metadata={})]}
[{'action': 'talk', 'action_input': {'agent_name': 'George', 'message': "Let's go to the forest and collect some apples to trade with other agents at the market when it opens."}}]
Finished in 13.0836s
```

We test it for the sample setup 5 times, 4 of the outputs are trying to talk with itself, only a single one is reasonable `go_to market`. The average running time is \~8s.

We have test to include the Qwen LLM inside of langchain, currently it cannot stop at the position we want and it's even slower. (Should we still go ahead to fix and test it?)

## Socket Communication

To communication with the rendering and executing loop in Godot, a socket setup is build and used as the core loop in `main.py`.

To simulate the godot part, a testing client is provided in `tests/socket_communication.py`.

Usage:

```bash
export PYTHONPATH=/path/to/this/project/folder

# start server
python main.py --host localhost --port 33455

# test with testing client
python tests/socket_communication.py --host localhost --port 33455
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
