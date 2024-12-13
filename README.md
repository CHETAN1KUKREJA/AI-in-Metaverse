# LLM-Backend

## Prompt Engineering

We provide 3 modes: simple_chain, guided_chain and deep_guided_chain. The latter two modes are implemented to guide the LLM to extract information using manually designed steps to suppress hallucination. Thus, they are more explainable and controllable. But the deep_guided_chain outputs more intermediate steps and therefore can be slower and memory consuming. The default mode is set to guided_chain.

### Example Prompt

Here is an example prompt from the `test_json.json`.

```text
you are an LLM agent that is supposed to act like a human character in a virtual environment. you are given some set of actions and your job is to choose the most relevant sequence of actions in order to carry out a task in the environment.

### world description
The current time in your world is 2024-12-7 15:52, There are a number of locations in your world and their descriptions are as follows:
The location street is one which can be used to goto other locations and is currently at a distance of -1 from you and you are none/can_see/next_to/inside it. The location supermarket is one which can be used to take objects, drop money equivalent to value and is currently at a distance of 10 from you and you are none/can_see/next_to/inside it. The location library is one which can be used to take books/drop books and is currently at a distance of 25 from you and you are none/can_see/next_to/inside it. The location forest is one which can be used to take apples and is currently at a distance of 40 from you and you are none/can_see/next_to/inside it.

### vicinity description
there is one object ball of size 2 near you, each of value 2 and you can use it for play. you are not the owner. there is an agent <agentName> at a distance 10 to you. 
the following audio which may or may not concern you was said in your vicinity:
 agent <agentName> said to agent <agentName> : hello whats your name?.

### agent description

Your current status:
- Health: 10
- Hunger: 3
- Happiness: 5
- Age: 23
- Current Location: street
- Current Action: goTo(library) (50% completed)
- Items in Hand: pen (1)
- Inventory: money (25), apple (1)
- Ownership: money (25), apple (1), house1 (1), house2 (1)

### contracts description

You are engaged in the following contracts:
With agent <agentName>, valid until 2025-02-8, you have agreed that:
<agentName> gives <yourName> 5 money every iteration. <yourName> gives <agentName> 2 apples every iteration.

### system description
0. Another agent "Marie" was talking, and what you just said "Hello!" is covered. You may need to repeat it.
1. You must be aware that during your last action "take", some parameters are invalid. Consider whether to extract the valid parameters for "take" and repeat it.
2. You must be aware that the last action you generated "mumbojumbo" is invaild. You are not allowed to perform it.
3. You must be aware that the last action you generated "exit" is invaild. You are not allowed to perform it.
4. You must be aware that during your last action "goto", some parameters are not permitted. Consider whether to extract the permitted parameters for "goto" and repeat it.

### actions description
Duration descriptor is -1 means that the
The set of actions available to you are: 
{"name": "goTo", "description": "goto a location. The duration is not fixed, it depends on where to go", "duration": -1, "parameters": [{"name": "location", "type": "string", "description": "the target location"}]}
{"name": "take", "description": "take something", "duration": 1, "parameters": [{"name": "objectName", "type": "string", "description": "The object name to take"}]}
{"name": "drop", "description": "drop something", "duration": 1, "parameters": [{"name": "objectName", "type": "string", "description": "The object name to drop"}]}
{"name": "talk", "description": "talk to nearby agents. If you want to talk to someone, add his name in the content", "duration": 1, "parameters": [{"name": "volume", "options": ["whisper", "normal", "shout"], "type": "string", "description": "The volume you should talk"}, {"name": "content", "type": "string", "description": "The content you talk"}]}

### end of description
That's all the information you know for now. If you need information from other agents, you should ask them and wait them to reply. You are not allowed to assume anything yourself.

### goal
Your goal is always to maximise the amount of money that you have and generate a valid sequence of actions you choose to do at that particular instant of time.

The output you must generate must be a Chain-of-thoughts which consist of valid thought action pairs in a specific sequence. For each action you pick you must give an explanation as to why you chose it and finally combine all the actions to form a list/sequence and output it after the Chain-of-thoughts. The final sequence must be a valid JSON response within XML tags <tool_call></tool_call> with function name and arguments:

<tool_call>
{"name": <function-name>(, "arguments": <args-json-object>)}
{"name": <function-name>(, "arguments": <args-json-object>)}
</tool_call>
```

### Testing

We provide the `prompt_engineering.py` to test the prompt. You can either simply output the prompt or test it on a local LLM. Currently tested models are:

* unsloth/Llama-3.3-70B-Instruct-bnb-4bit
* meta-llama/Meta-Llama-3.1-8B-Instruct
* katanemo/Arch-Function-3B

### Sample Result

Using the `test_json.json`, here are the an outputs from Llama-3.3-70B-Instruct-bnb-4bit with simple_chain mode:

```md
To maximize the amount of money I have, I need to consider the available actions and the current state of the environment. Here's my chain of thoughts:

1. **Assess Current State**: I am at the trade centre with 50 euros and 20 apples. There's another agent, Maria, also at the trade centre. This information is crucial because it suggests potential trade opportunities.

2. **Consider Trading**: Since I have apples and euros, and there's another agent nearby, trading could be beneficial. However, to initiate a trade, I might need to communicate with Maria.

3. **Choose Action - Talk**: To communicate with Maria about a potential trade, I should use the "talk" action. This action allows me to convey my interest in trading and negotiate terms.

4. **Determine Trade Details**: Before talking, I should decide what I'm willing to trade (apples for euros or vice versa) and what ratio seems fair. Given that I have 20 apples and 50 euros, and without knowing the market demand or supply, a straightforward approach could be to offer a direct trade based on equal value, if possible.

5. **Execute Talk Action**: With the "talk" action, I'll approach Maria and propose a trade. The volume can be "normal" since we are in the same location, and the content will include my proposal, such as "Hello Maria, I have 20 apples and 50 euros. Would you like to trade?"

6. **Potential Next Steps**: Depending on Maria's response, the next actions could involve agreeing on a trade, which might require using the "take" and "drop" actions to exchange goods, or renegotiating terms if the initial proposal isn't acceptable.

Given these considerations, my initial action will be to talk to Maria to propose a trade. Here is the sequence of actions I've decided on so far, formatted as requested:

<tool_call>
{"name": "talk", "arguments": {"volume": "normal", "content": "Hello Maria, I have 20 apples and 50 euros. Would you like to trade?"}}
</tool_call>
Finished in 147.8059s
```

Another output from Llama-3.3-70B-Instruct-bnb-4bit with guided_chain mode:

```md
### Step 0: Analysis with the given information

From the provided information, we understand the following key points:

1. **Current Status**: We have a health of 10, hunger of 3, happiness of 5, and we are 23 years old. We are currently located on the "street".
2. **Inventory and Ownership**: We have a pen in hand, an inventory consisting of money (25 units) and an apple, and we own two houses (house1 and house2).
3. **Contracts**: We are engaged in a contract with another agent where we receive 5 money every iteration and give 2 apples in return.
4. **Available Actions**: We can perform actions like "goTo" (to move to different locations), "take" (to pick up objects), "drop" (to drop objects), and "talk" (to communicate with nearby agents).
5. **Goal**: Our primary objective is to maximize the amount of money we have.

Given our current situation and the goal, our immediate plan should focus on addressing our hunger (since it's at 3) and exploring ways to increase our wealth. 

Since we are currently on the "street" and our hunger is at 3, it might be beneficial to head towards the "supermarket" to acquire food, which could potentially increase our hunger satisfaction. However, we should also consider the distance to the supermarket (10 units away) and the fact that we are already in the process of going to the library (50% completed). It might be more efficient to complete our current action before diverting to the supermarket.

Additionally, interacting with the agent 10 units away from us could provide opportunities for trade or other beneficial interactions, given we have a contract that involves exchanging goods (apples for money).

### Step 1: Identify sequential key actions

Based on our analysis, the key actions could be:
1. **Complete the current action of going to the library**: Since we are already 50% into this action, it might be more efficient to complete it before starting a new one.
2. **Address hunger**: This could involve going to the supermarket to acquire food. However, we need to consider the cost and the distance.
3. **Interact with the nearby agent**: Given the contract we have, interacting with other agents could lead to opportunities for gaining more money or resources.

For the action of going to the library, the required parameter is the location, which is "library".

For addressing hunger, if we decide to go to the supermarket, the action would be "goTo" with the location parameter being "supermarket".

For interacting with the nearby agent, we could use the "talk" action. The parameters for this action would include the volume (let's choose "normal" for a standard conversation) and the content (we could say "hello" to initiate a conversation).

### Step 2: Format function calls as JSON objects within XML tags

```xml
<tool_call>
    {"name": "goTo", "arguments": {"location": "library"}}
    {"name": "goTo", "arguments": {"location": "supermarket"}}
    {"name": "talk", "arguments": {"volume": "normal", "content": "hello"}}
</tool_call>
```

However, it's crucial to note that we should prioritize these actions based on our current situation and the distances involved. Completing the current action and then reassessing our situation might be the most logical first step. 

Therefore, the immediate next step should focus on completing the "goTo" library action, followed by a reassessment of our situation to decide whether to proceed to the supermarket or interact with the agent, considering the distances and our current needs.
Finished in 252.6397s
```

For other outputs, you can refer to the sample_outputs folder. A trend is bigger models output more accurate results, but they are slower. Smaller models are mostly inaccurate and have hallucinations, but they are fast (enough?).

TODO:

To fix this, discuss for the moment, short and long term planing.