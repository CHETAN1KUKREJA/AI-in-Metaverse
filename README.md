
# Memory System for Generative Agents

LLMs alone predict only next word based on a given prompt/input. This can lead to undesirable behavior and hallucination. This module implements a memory system designed for agents in the metaverse, enabling them to have personalities, remember past events, and make informed decisions. The memory system is inspired by the [Generative Agents: Interactive Simulacra of Human Behaviour](https://arxiv.org/abs/2304.03442) paper, while many changes have been made to it. 

The memory system consists of three types of memory: **Static Memory**, **Short-Term Memory**, and **Long-Term Memory**. All memory types are powered by the [`chromadb`](https://docs.trychroma.com/docs/overview/getting-started) AI database. Each memory subtype is organized into a separate collection within a persistent storage directory, ensuring efficient management and retrieval.

---
### Memory Structure
All agent memories are stored as persistent binaries in the `./database/mem_test/<agent_name> folder.` Each memory entry includes three components: `doc` containing the memory string or detail, `metadata` with attributes such as `importance_score` and `timestamp`, and a `unique id` to prevent overwriting. Static memory is immutable and contains essential information about the agent, including its identity, world rules, and environment description. These are stored as JSON files in the `./agent_personalities/<agent_name>.json` path and are loaded during simulation. Static memory is unaffected by decay and is the first memory queried by the agent before short-term or long-term memory. Short-term memory (STM) acts as the initial storage for perceived events, such as environmental data and conversations. Each event has an associated timestamp, which is used to compute an initial score based on recency and importance. STM entries are added or overwrite existing ones with the same id to reduce redundancy. A memory is considered relevant if its total score exceeds the threshold, empirically set at 0.35. If STM contains more than `k` entries, the most important memories are migrated to long-term memory (LTM) if the `migrate_STM2LTM` function is invoked. During migration, entries are deleted from STM and added to LTM only if their importance_score exceeds the threshold. The agent can also reflect, plan, and summarize multiple long-term memories into a new consolidated memory, enabling efficient memory management and improved contextual understanding.

---
## Abstract Memory Class

The memory system is designed as an abstract class, serving as a blueprint for all core memory-related operations by providing placeholder functions. This modular design enables developers to easily extend functionality and implement new types of memory systems as needed. Additionally, a `MemoryEntry` dataclass is included to streamline the process of handling single document entries, ensuring consistency and simplicity in memory storage and retrieval.

### Key Features:
- **Abstract Class**: Defines the core structure and necessary methods for any memory system.
- **ChromaMemory Implementation**:
  - A child class of the abstract memory class, specifically designed to integrate with `chromadb`.
  - Implements the abstract methods with the `chromadb` specifications.
- **Future Flexibility**:
  - Developers can easily migrate to other databases by implementing a new child class of the abstract memory class.
  - Ensures modularity and adaptability of the system for different backends.

---
## Memory Types

### 1. **Static Memory**
- **Purpose**: Stores unchanging information about the agent, such as:
  - Identity (name, age, profession, etc.)
  - Long-term goals
  - Societal rules
  - Environmental details (e.g., map-based data)
  - Trust scores
- **Storage**: Some predefined personalities are stored in `./agent_personalities/<agent_name>.json`.
- **Key Features**:
  - Queried first by the agent for any decision-making.
  - Not subject to memory decay.

### 2. **Short-Term Memory (STM)**
- **Purpose**: Temporarily stores recent events, such as interactions and observations.
- **Storage**: Persisted in `./database/mem_test/<agent_name>` as binaries, with the following components:
  - **Document**: Memory content.
  - **Metadata**: Includes `importance_score` and `timestamp`.
  - **Unique ID**: Prevents duplication.
- **Behavior**:
  - Events are added to STM with an initial `importance_score` based on recency and personal impact.
  - STM size can be adjusted (`stm_size`), and older, less relevant memories are replaced as needed.
  - Queried when Static Memory lacks sufficient context.

### 3. **Long-Term Memory (LTM)**
- **Purpose**: Stores significant memories over extended periods.
- **Behavior**:
  - Memories migrate from STM to LTM if their `importance_score > threshold` (only when migration function is invoked).
  - There is no way to insert in to the LTM directly. It always has to pass through STM first.
  - Supports reflection and summarization to condense multiple memories into meaningful insights.

---

## Memory Features

### 1. **Memory Migration**
- **Function**: `migrate_stm2ltm`
- **Purpose**: Transfers the oldest and most important entries from Short-Term Memory (STM) to Long-Term Memory (LTM), provided their `importance_score` exceeds a predefined threshold.
- **Behavior**: Once an entry is successfully migrated, it is deleted from STM to maintain efficiency and prevent redundancy.

### 2. **Summarization and Forgetting**
- **Function**: `summarize_and_forget`
- **Purpose**: Summarizes the least important LTM entries to prevent unbounded growth.
- **Behavior**: Uses an LLM to condense memories and reinserts the summary into LTM.

### 3. **Reflection from Recent Memory**
- **Function**: `reflect_from_recent_memory`  
- **Purpose**: Extracts high-level insights from short-term memories (STM) and consolidates them into meaningful reflections.  
- **Process**:  
  1. **Generate High-Level Insights**:  
     - A LLM analyzes selected documents from STM to derive high-level insights and formulates a relevant question.  
  2. **Retrieve Context**:  
     - The memory system queries additional documents to provide context for answering the generated question.  
  3. **Answer the Question**:  
     - The LLM uses the retrieved context to answer the question, producing a concise reflection.  
  4. **Store the Reflection**:  
     - The generated reflection is stored as a new memory entry, enhancing the agent's ability to reason and recall summarized insights.  


### 4. **Action Planning**
- **Function**: `plan_from_memory`. Hosted at [http://127.0.0.1:5000/plan](http://127.0.0.1:5000/plan)
- **Purpose**: Creates short-term plans for the agent.
- **Behavior**: Queries relevant context from memories and uses an LLM to formulate a plan, which is added to LTM.

### 5. **Memory Querying**
- **Function**: `query_memory`
- **Purpose**: Retrieves relevant context based on input prompts.
- **Behavior**:
  - Priority order: Static Memory → Short-Term Memory → Long-Term Memory.
  - Uses recency, importance, and cosine similarity for scoring.
  - Retrieves `top_k` memories with a score above a set threshold (default: `0.35`).

### 6. **Importance Scoring**
- **Function**: Hosted at [http://127.0.0.1:5000/rate](http://127.0.0.1:5000/rate)
- **Purpose**: Rates memory significance on a scale of 1 to 10. For every event in the memory, it rates on a scale from 0 to 10, which memories are mundane and which induce strong emotion or have high significance. 
- **Behavior**: LLM evaluates the memory with the following prompt:
    ```python
    "On the scale of 1 to 10, where 1 is purely mundane "
    "(e.g., brushing teeth, making bed) and 10 is extremely poignant "
    "(e.g., a break-up, college acceptance, life), rate the likely poignancy of the "
    f"following piece of memory.\nMemory: {memory}\n"
    "Provide just your rating a single number rating:<fill_in> and a explanation in JSON format like this: "
    '{"explanation": ...,"rating":.. }'
    "provide only 1 json"
    ```

---

## Retrieval Score Calculation

The memory score is calculated as:  
$$ \text{score} = \alpha_{\text{recency}} \cdot \text{recency} + \alpha_{\text{importance}} \cdot \text{importance} + \alpha_{\text{relevancy}} \cdot \text{relevancy} $$

> If the score is not present in the metadata, the function then reduces to only relevancy, i.e., the agent queries only the memories that has the most similar embedding/meaning to the given promt.


#### **Weights**:
- $\alpha_{\text{recency}} = 0.25$
- $\alpha_{\text{importance}} = 0.25$
- $\alpha_{\text{relevancy}} = 1.00$

These weights were selected as they empirically yielded credible and reliable results. *(Note: These values are subject to adjustment if a better combination is identified in the future.)*

#### **Components**:
1. **Recency**:
   - Scaled between 0 and 1.
   - Memories created or accessed less than 60 minutes ago are given the highest weight.
   - Computed using an exponential decay function: `k^(time_diff_in_hours)`, where \( k \) is the decay factor.

2. **Importance**:
   - Calculated using a LLM when inserting any document into the memory

3. **Relevancy**:
   - Based on embedding similarity.
   - Default embedding model: `all-MiniLM-L6-v2`.
   - The similarity is calculated using the `chromadb` querying mechanism, which supports multiple embedding functions. A full list of supported embedding functions can be found [here](https://docs.trychroma.com/docs/embeddings/embedding-functions).
   - By default, the distance function is L2 (Euclidean distance), but cosine distance can also be used. For more details, see the [documentation](https://cookbook.chromadb.dev/core/collections/).
   - The final similarity score is computed as:

     $$ \text{similarity} = \frac{1}{1 + \text{distance}} $$


---

## Project Structure
- **`/database/`**: Stores persistent memory databases.
- **`/agent_personalities/`**: Contains static memory as JSON files.
- **`/memory_system/`**: Memory system implementation files.

---

## How to Use
1. Populate static memory using JSON files in the `agent_personalities/` directory.
2. Add new events to STM using the `MemoryEntry` dataclass or JSON format.
3. Call `migrate_stm2ltm`, `summarize_and_forget`, or `reflect_from_recent_memory` as needed to manage memory transitions.
4. Query memory using the `query_memory` function with an input prompt.

---

## Specifications/Model Zoo
- **Embedding Model**: `all-MiniLM-L6-v2` (default)
- **Distance Metric**: Cosine similarity
- **Performance**:
  - Efficient retrieval with `chromadb`.
  - Memory decay and reflection mechanisms prevent unbounded growth.

---

## Future Work
- Finalize project structure.
- Optimize scoring weights. (Hyper parameter fine tuning)
- Define better Agent Personalities
- Try out a new type of memory system by combining the current system with reinforcement learning to let the system "learn" what memories are important and should last longer, and which can fade away.
- Look into Temporal Neural Networks for more advanced models of memory decay.
- Work on defining what should go into what memory. for eg, should procedural step of function calling go into memory?
