## Memory Explained
LLM alone predicts only next words based on the given prompt/input and can lead to undesirable behaviours and hallucination. Thus, memory system is crucial for storing and retrieving the information one agent can access, which will be fed to our agents to make any decision. Our memory system is inspired by the [Generative Agents: Interactive Simulacra of Human Behaviour](https://arxiv.org/abs/2304.03442) paper, and consist of 3 types: 1) Static Memory, 2) Short Term Memory, and 3) Long-term memory, all powered by [`chromadb`](https://docs.trychroma.com/docs/overview/getting-started) AI database. 

### Memory Type

All of the memories of the agent are stored as persistent binaries found in `./database/mem_test/<agent_name>` folder. Each have 1) `doc` containing the memory string/detail, 2) `metadata` such as `importance_score`, and `timestamp`, and 3) unique `id` to prevent overwriting.

The static memory is the memory that will not be changed overtime. It contains information about the agent's identity, rules of the world, and the description of the environment. This can be found at path `./agent_personalities/<agent_name>.json` and is stored as `JSON` files to be loaded during simulation. They are unaffected from the memory decay and are the most important memory that Agent will query before the short-term or long-term memory.

Short-term memories are the first storage of every events that the agents can perceive. This include data about environments in the game, conversation etc. Every event is associated with a timestamp, which is used to calculate the initial score based on recency and personal importance (see this [Sec.](#maths-behind-our-system)). The memories are then either added to the memory, or overwrite the existing ones to prevent multiple ids of the same timestamps and lower redundancy. This is the second memory the agent will query if there are not enough matched context from the static memory. The memory is considered matched with the given prompt if the total score is higher than the threshold, which is emperically set at `0.35`.

After some time and short-term memory has `>3` entries, the agent can move the most important memories from short- to long-term. The document will be deleted from the short-term and then added to the long-term memory database *ONLY* if the memory `importance_score > 0.5`.

In addition, long-term memory have decay mechanism, which exponentially reduce the importance score as time goes by. The agent can also reflect and summarize multiple long-term memories into a new one.

### How is the Score Calculated
Following the paper mentioned, we calculate the total score based on 1) relevancy/embedding similariy, 2) recency, and 3) importance/personal impact. Specifically:
$$ score = \alpha_{recency}recency + \alpha_{importance}importance + \alpha_{relevancy}relevancy $$

> If the score is not present in the metadata, the function then reduces to only relevancy, i.e., the agent queries only the memories that has the most similar embedding/meaning to the given promt. 

where $\alpha_{recency}=0.25$, $\alpha_{importance}=0.25$, and $\alpha_{relevancy}=1$, which we find to produce believable result. (tbd: change if better combination of value is found).

Recency is calculated on scale 0 to 1 where 1 means the memory is <60 min. old, and the factor of $\gamma=<insert>$ is multiplicatively applied for every game-hour passed since the associated timestamp.

Meanwhile, the importance is generated through the LLM rater instance hosted in the server and can be accessed through the link [http://127.0.0.1:5000/rate](http://127.0.0.1:5000/rate). For every event in the memory, it rates from scale 0 to 10 which memories are mundane and which induce strong emotion or has high significance. The full prompt for this is:
```python
"On the scale of 1 to 10, where 1 is purely mundane "
"(e.g., brushing teeth, making bed) and 10 is extremely poignant "
"(e.g., a break-up, college acceptance, life), rate the likely poignancy of the "
f"following piece of memory.\nMemory: {memory}\n"
"Provide just your rating a single number rating:<fill_in> and a explanation in JSON format like this: "
'{"explanation": ...,"rating":.. }'
"provide only 1 json"
```

Lastly, the similarity is calculated based on the embedding distances implemented by the `chromadb` querying mechanism. There are many supported embedding functions, which can be found [here](https://docs.trychroma.com/docs/embeddings/embedding-functions), but `all-MiniLM-L6-v2` is set as default. The default distance function is L2 (Euclidean distance), but cosine distance is also possible (see [docs](https://cookbook.chromadb.dev/core/collections/)). The final similarity score is:
$$similiarity = \frac{1}{1+distance}$$

### Retrieval
- The agent querys for `top_k` memories with the highest score, with priority from most to least: static -> short-term -> long-term. 
- If the calculated score of queried memory is less than the set threshold `0.35`, those memories will not be added to the context with the prompt for later action generation.
- The querying will stop immediately if there are `top_k` memories found with score > threshold and the memory type with less priority will not be considered.

## Project Structure
tbd after finalization



## How to use
tbd

## Specs/Model Zoo
- Model used
- Memory, performance, time etc.