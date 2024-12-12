# LLM-Backend

## Prompt Engineering

TODO: merge progress

We provide 3 modes: simple_chain, guided_chain and deep_guided_chain. The latter two modes are implemented to guide the LLM to extract information using manually designed steps to suppress hallucination. Thus, they are more explainable and controllable. But the deep_guided_chain outputs more intermediate steps and therefore can be slower and memory consuming. The default mode is set to guided_chain.

### Testing

We provide the `prompt_engineering.py` to test the prompt. You can either simply output the prompt or test it on a local LLM. Currently tested models are:

* unsloth/Llama-3.3-70B-Instruct-bnb-4bit
* meta-llama/Meta-Llama-3.1-8B-Instruct
* katanemo/Arch-Function-3B

### Sample Result

Using the `test_json.json`, here are the some outputs:

#### Llama-3.3-70B-Instruct-bnb-4bit with simple_chain mode:

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

#### Llama-3.3-70B-Instruct-bnb-4bit with guided_chain mode:

```md
### Step 0: Analysis and Planning                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                   
Given the current situation, my goal is to maximize the amount of money I have. I am currently at the trade centre with 50 euros and 20 apples. There is another agent, Maria, also at the trade centre. To achieve my goal, I need to gather more information about the current ma
rket conditions and potential trades. Since I don't have enough information about what Maria has or what she is willing to trade, my first step should be to communicate with her. The action "talk" seems most appropriate for this purpose. I will ask Maria about her current in
ventory and what she is willing to trade.                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                   
### Step 1: Identify Sequential Key Actions                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                   
1. **Talk to Maria**: To gather information about her inventory and potential trades.                                                                                                                                                                                              
2. **Assess Trade Opportunities**: Based on Maria's response, decide if there's a beneficial trade to be made.                                                                                                                                                                     
3. **Execute Trade (if beneficial)**: Use the "take" and "drop" actions to exchange goods if a beneficial trade is found.                                                                                                                                                          

I chose these actions because they directly contribute to my goal of maximizing my money by potentially allowing me to make profitable trades. The "talk" action is essential for gathering necessary information, and "take" and "drop" are crucial for executing any trade that m
ight be agreed upon.                                                

### Step 2: Extract/Generate Parameters and Contents                

For the "talk" action:                                              
- **Volume**: "normal" seems appropriate for a trade negotiation.                                                                        
- **Content**: "Hello Maria, what are you willing to trade?"                                                                             

For potential "take" and "drop" actions, the parameters will depend on the outcome of the negotiation with Maria. For example:                                                                                                                                                     
- If Maria agrees to trade 5 of her apples for 10 euros, the actions would be:                                                           
  - **Take**: "10 euros"                                            
  - **Drop**: "5 apples"                                            

However, these are speculative and depend on the negotiation outcome.                                                                    

### Step 3: Format Function Calls as JSON Objects within XML Tags                                                                        

Given the initial step of talking to Maria, the function call would be:                                                                  

<tool_call>                                                         
{"name": "talk", "arguments": {"volume": "normal", "content": "Hello Maria, what are you willing to trade?"}}                            
</tool_call>                                                        

Subsequent actions will be determined based on Maria's response and will follow a similar format for "take" and "drop" actions if a trade is agreed upon.                                                                                                                          
Finished in 156.1652s
```

#### Llama-3.3-70B-Instruct-bnb-4bit with deep_guided_chain mode:

```md
## Step 0: Plan what to do for a short period                       
To maximize the amount of money, the first step is to gather information about the current state of the trade centre and the forest. Since there is another agent, Maria, at the trade centre, it might be beneficial to interact with her to see if there are any trade opportunit
ies. The plan is to:                                                
1. Talk to Maria to gather information about her current stock of apples and money.                                                      
2. Ask Maria if she is willing to trade apples for money.           
3. If a trade is possible, negotiate the terms of the trade.                                                                             
4. If no trade is possible with Maria, consider going to the forest to collect apples.                                                   

## Step 1: Extract a sequence of actions and parameters pairs from the plan                                                              
### Substep 1.1.1: Output description of the action                 
1. Action: talk                                                     
2. Parameters: volume, content                                      
3. list:                                                            
- Talk to Maria to gather information about her current stock of apples and money.                                                       
- Ask Maria if she is willing to trade apples for money.            

### Substep 1.1.2: Verify the action and parameters                 
1. The action "talk" appears in the plan.                           
2. The sentences covering the action and parameters appear in the plan.                                                                  
3. The parameter "content" might need to be specified based on Maria's response, which will be answered by her.                          
Considering the need to interact with Maria first, the sequence of actions starts with talking to her.                                   

## Step 2: Format the plan as function calls in JSON objects within single XML tags                                                      
Given the plan and the actions available, the first step is to talk to Maria. The function call for this action is:                      

<tool_call>                                                         
{"name": "talk", "arguments": {"volume": "normal", "content": "Hello Maria, what are you trading today?"}}                               
</tool_call>                                                        

This initial interaction is aimed at gathering information and setting the stage for potential trades or other actions based on Maria's response. Further actions will depend on her answer, which could involve negotiating a trade, deciding to go to the forest, or other option
s based on the information exchanged.                               
Finished in 162.5875s
```

#### Meta-Llama-3.1-8B-Instruct with simple_chain mode

We can observe a huge hallucination here.

```md
Chain-of-thoughts:                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                   
I need to maximize my money, and I currently have 50 euros and 20 apples. I'm at the trade centre, which means I have a chance to trade with other agents. I see Maria at the trade centre, so I should try to talk to her and see if we can make a trade.                         
                                                                                                                                                                                                                                                                                   
First, I need to talk to Maria to initiate a trade. I'll use the "talk" action to do this. I'll choose the "normal" volume and a content that invites her to trade.                                                                                                                
                                                                                                                                                                                                                                                                                   
<tool_call>                                                                                                                                                                                                                                                                        
{"name": "talk", "arguments": {"volume": "normal", "content": "Hey Maria, want to trade apples for euros?"}}                                                                                                                                                                       
</tool_call>                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                   
Now, I need to wait for Maria's response. Once she responds, I'll proceed accordingly.                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                   
Assuming Maria agrees to trade, I'll need to determine the terms of the trade. If she has apples and I have euros, I should offer to trade my apples for her euros.                                                                                                                
                                                                                                                                                                                                                                                                                   
After the trade, I'll have a new amount of money and apples. If I have more apples than I can carry, I should consider going to the forest to collect more apples.                                                                                                                 
                                                                                                                                                                                                                                                                                   
However, since I'm at the trade centre, I should check if there are any other agents nearby who might be willing to trade. If not, I can consider going to the forest.

For now, let's assume Maria agrees to trade.

Next, I need to determine the number of apples I want to trade. I have 20 apples, and I want to maximize my money. I'll offer to trade 10 apples for her euros.

<tool_call>
{"name": "talk", "arguments": {"volume": "normal", "content": "I'll give you 10 apples for 10 euros."}}
</tool_call>

Now, I'll wait for Maria's response.

Assuming she agrees to the trade, I'll proceed with the trade.

<tool_call>
{"name": "take", "arguments": {"objectName": "10 apples"}}
</tool_call>

<tool_call>
{"name": "drop", "arguments": {"objectName": "10 apples"}}
</tool_call>

<tool_call>
{"name": "take", "arguments": {"objectName": "10 euros"}}
</tool_call>

Now, I have 10 euros and 10 apples. I should go to the forest to collect more apples.

<tool_call>
{"name": "goTo", "arguments": {"location": "forest"}}
</tool_call>

Final sequence of actions:

<tool_call>
{"name": "talk", "arguments": {"volume": "normal", "content": "Hey Maria, want to trade apples for euros?"}}
</tool_call>

<tool_call>
{"name": "talk", "arguments": {"volume": "normal", "content": "I'll give you 10 apples for 10 euros."}}
</tool_call>

<tool_call>
{"name": "take", "arguments": {"objectName": "10 apples"}}
</tool_call>

<tool_call>
{"name": "drop", "arguments": {"objectName": "10 apples"}}
</tool_call>

<tool_call>
{"name": "take", "arguments": {"objectName": "10 euros"}}
</tool_call>

<tool_call>
{"name": "goTo", "arguments": {"location": "forest"}}
</tool_call>
Finished in 37.9471s
```