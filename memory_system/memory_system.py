from . import base_memory
from .base_memory import MemoryEntry
import dspy
import time
from datetime import datetime
import math
import json
import requests
import os

class AgentMemory:
    """
    This a complex memory system that stores data in three different memory stores: static, short-term, and long-term.
    
    This Memory System is designed to be used by an agent to store and manage memories in a more sophisticated manner
    while trying to mimic human memory processes.
    
    The memory system has the following features:
    - Importance score for each memory calculation based on recency and personal impact by using a small LLM model
    - Migrate the oldest Memories from short-term memory to long-term memory
    - Summarize and forget the least important memories in long-term memory
    - Get statistics of the memory
    - Reset all memory stores
    - Query the memory system for relevant context based on the input prompt
    - Reflect from recent memory
    - Plan an action based on the context from memories and add it to long-term memory
    """
    def __init__(self, base_client_path, agent_name, URI_RATING = "http://127.0.0.1:5000/rate", URI_PLANNING = "http://127.0.0.1:5000/plan",verbose=False):
        self.agent_name = agent_name
        self.static_memory = base_memory.ChromaMemory(name="StaticMemory", verbose=verbose)
        self.short_term_memory = base_memory.ChromaMemory(name="ShortTermMemory", verbose=verbose)
        self.long_term_memory = base_memory.ChromaMemory(name="LongTermMemory", verbose=verbose)
        self.reflection_memory = base_memory.ChromaMemory(name="ReflectionMemory", verbose=verbose)
        self.plan_memory = base_memory.ChromaMemory(name="PlanMemory", verbose=verbose)
        self.stm_size = 10
        self.URI_RATING = URI_RATING
        self.URI_PLANNING = URI_PLANNING
        self.verbose = verbose
        self.base_client_path = base_client_path
        self._initiate_memory()
        return

    def add_short_term(self, input_data, overwrite_existing=False):
        """
        Adds a memory to the memory system.
        
        :param input_data: Either a JSON file path or a dictionary containing the memory data
        :param overwrite_existing: Whether to overwrite existing memories with the same ID
        """
        if isinstance(input_data, str):
            # Check if the path is a JSON file and if it exists
            if not input_data.endswith('.json'):
                raise ValueError("Provided file path is not a JSON file.")
            if not os.path.exists(input_data):
                raise FileNotFoundError(f"The file {input_data} does not exist.")

            # Load from JSON file
            with open(input_data) as f:
                data = json.load(f)
                documents = data['documents']
                metadatas = data['metadatas']
                ids = data['ids']
        elif isinstance(input_data, MemoryEntry):
            # Single document input
            documents = input_data.documents
            metadatas = input_data.metadatas
            ids = input_data.ids
        else:
            raise ValueError("Invalid input_data format. Must be a JSON file path or a dictionary.")
        
        for meta in metadatas:
            curr_time = datetime.now().isoformat()
            meta["timestamp"] = str(curr_time)
            importance_score = self._initial_recency_and_importance_score_calculator(input_data, curr_time)
            meta["importance_score"] = importance_score
            

        existing_ids = set(self.short_term_memory.memory.get()["ids"])
        new_documents = []
        new_metadatas = []
        new_ids = []

        for doc, meta, id_ in zip(documents, metadatas, ids):
            if id_ in existing_ids:
                if overwrite_existing:
                    self.short_term_memory.delete_memory(keys=[id_])
                    new_documents.append(doc)
                    new_metadatas.append(meta)
                    new_ids.append(id_)
                else:
                    pass
                    # print(f"Skipped adding memory with ID: {id_} (already exists)")
            else:
                new_documents.append(doc)
                new_metadatas.append(meta)
                new_ids.append(id_)

        if new_ids:
            self.short_term_memory.memory.add(
                documents=new_documents,
                metadatas=new_metadatas,
                ids=new_ids,
            )
            print(f"Added {len(new_ids)} short term memories successfully.")
        else:
            print("No new memories added.")

        return

    def migrate_stm2ltm(self, threshold=0.3):
        """
        Migrates the oldest document from short-term memory to long-term memory.
        The document is deleted from short-term memory after migration.
        
        Returns:
            bool: True if migration was successful, False if no documents to migrate
        """
        # Get all documents from short-term memory
        stm_data = self.short_term_memory.memory.get()
        
        length_stm = len(stm_data['documents'])
        
        # Check if there are any documents to migrate
        if length_stm <= self.stm_size:
            print("Not enough documents to migrate to long-term memory")
            return
            
        # Zip together documents, metadata, and ids for easier processing
        memory_entries = list(zip(
            stm_data['documents'], 
            stm_data['metadatas'], 
            stm_data['ids']
        ))
        
        # Sort by timestamp in ascending order to get the oldest entry
        oldest_entries = sorted(
            memory_entries,
            key=lambda x: x[1]['timestamp']
        )[:length_stm-self.stm_size]
        
        for i in range(len(oldest_entries)):
        
            oldest_document, oldest_metadata, oldest_id = oldest_entries[i]
            
            self.short_term_memory.delete_memory(keys=[oldest_id])
            
            if(oldest_metadata['importance_score'] < threshold):
                continue
            
            # Create new ID for long-term memory
            ltm_id = f"ltm_{oldest_metadata['timestamp']}"
            
            try:
                self.long_term_memory.memory.add(
                    documents=[oldest_document],
                    metadatas=[oldest_metadata],
                    ids=[ltm_id]
                )
                
                print(f"Successfully migrated memory from short-term to long-term: {oldest_document}")
                
            except Exception as e:
                print(f"Error during migration: {str(e)}")
        return
    
    def summarize_and_forget(self, k=5):
        """
        
        Summarize the k least important memories in the long-term memory and delete them.
        
        Args:
            k (int): Number of least important memories to summarize and delete
        """
        ltm_data = self.long_term_memory.memory.get()
        if len(ltm_data['documents']) >= k:
            ltm_entries = list(zip(
                ltm_data['documents'],
                ltm_data['metadatas'],
                ltm_data['ids']
            ))
            
            least_important = sorted(
                ltm_entries,
                key=lambda x: x[1]['importance_score']
            )[:k]
            
            combined_content = " ".join(entry[0] for entry in least_important)
            avg_importance = sum(entry[1]['importance_score'] for entry in least_important) / k
            
            try:
                # question = f"Summarize the following content in exactly two lines:\n{combined_content}"
                # gen = dspy.Predict('question -> answer')
                # summary = gen(question = question).answer
                
                question = f"Summarize the following content in exactly two lines:\n{combined_content}, give me output in JSON with this format" + "{message: <summary>}"
                # print(question)
                # gen = dspy.Predict('question -> answer')
                # summary = gen(question = question).answer
                
                response = requests.post(self.URI_PLANNING,json={'memory': question})
                response.raise_for_status()  # Raise an exception for bad status codes
                summary = response.json()
                if isinstance(summary, str):
                    summary = json.loads(summary)
                summary = summary['message']
                
                old_ids = [entry[2] for entry in least_important]
                self.long_term_memory.delete_memory(keys=old_ids)
                
                # Add consolidated summary
                new_metadata = {
                    'timestamp': time.time(),
                    'importance_score': avg_importance,
                    'type': 'consolidated_summary'
                }
                
                self.long_term_memory.memory.add(
                    documents=[summary],
                    metadatas=[new_metadata],
                    ids=[f"consolidated_{int(time.time())}"]
                )
                
                print(f"Successfully consolidated {len(least_important)} memories into summary")
                
            except Exception as e:
                print(f"Error during consolidation: {str(e)}")
                
        else:
            print("Not enough memories in long-term memory to consolidate")

    def reflect_from_recent_memory(self, top_k=10):
        """
        Consolidate high-level questions from short term memories into reflection summary.
        """
        stm_data = self.short_term_memory.memory.get()
        if len(stm_data['documents']) < top_k:
            print("Not enough memories in short-term memory to reflect")
            return
        
        stm_entries = list(zip(
                stm_data['documents'],
                stm_data['metadatas'],
                stm_data['ids']
            ))
            
        combined_content = " ".join(entry for entry in stm_data['documents'])
        avg_importance = sum(entry[1]['importance_score'] for entry in stm_entries) / len(stm_entries)
        
        try:
                question = f"What is a high-level insight that you can infer from the below statements? Reply with a question:\n{combined_content}, give me output in JSON with this format" + "{message: <summary>}"
                print("Vyom goel: ", combined_content)
                # gen = dspy.Predict('question -> answer')
                # summary_ques = gen(question = question).answer
                response = requests.post(self.URI_PLANNING,json={'memory': question})
                response.raise_for_status()  # Raise an exception for bad status codes
                summary = response.json()
                if isinstance(summary, str):
                    summary = json.loads(summary)
                summary_ques = summary['message']
                print("adawd QUESTION: ", summary_ques)
                docs = self.query_memory(summary_ques, top_k=5)
                print("fnoienfoewneif", docs)
                question = f"Given this question:\n{summary_ques}, and the following is the content:\n{docs}, give the final insight.give me output in JSON with this format" + "{message: <summary>}"
                # gen = dspy.Predict('question -> answer')
                # summary_ans = gen(question = question).answer
                response = requests.post(self.URI_PLANNING,json={'memory': question})
                response.raise_for_status()  # Raise an exception for bad status codes
                summary = response.json()
                if isinstance(summary, str):
                    summary = json.loads(summary)
                summary_ans = summary['message']

                # Add consolidated summary
                new_metadata = {
                    'timestamp': time.time(),
                    'importance_score': avg_importance,
                    'type': 'consolidated_summary'
                }
                
                self.reflection_memory.memory.add(
                    documents=[summary_ans],
                    metadatas=[new_metadata],
                    ids=[f"consolidated_{int(time.time())}"]
                )
                
                print(f"Successfully consolidated high-level questions from short term memories into reflection summary")
                
        except Exception as e:
                print(f"Error during consolidation: {str(e)}")

    def plan_from_memory(self, timestamp: str = None, top_k: int = 20, score_threshold: float = 0.4) -> None:
        """
        Plan an action based on the context from memories and add it to long-term memory.

        Args:
            timestamp (str): The timestamp of the current game time. Defaults to the current time if not provided.
            top_k (int): Number of top matches to retrieve from all memory.
            score_threshold (float): Threshold to filter out low score context.
        """

        prompt_for_context = """
            Answer the following question based on the context from memories:
            What is your name?
            What is the summary of your character and traits?
            What is your passion project currently, and how do you plan to achieve it?
            What actions did you do recently, up until 1 day ago?
        """

        context = self.query_memory(
            prompt_for_context, 
            top_k=top_k, 
            threshold=score_threshold
        )

        if timestamp is None:
            timestamp = datetime.now().isoformat()

        prompt_for_plan = f"""
            Based on the given context, fill in the following template. 
            Do not hallucinate. If you don't know the answer, say "I don't know".
            <goal_i> must have only following information: <time_i>, <action_i>, <location_i>, and <time_i> must contain date, hour, minute in ISO format, and must be in the future within today.
            Every action should not occur at the same time.Current time is {timestamp}.
            The other place holders can be normal text.
            Context: {context}

            Only return your answer as JSON string in the following format:
        """
        append_str = """
            {'plan':
                goal_1:
                    action: <action_1>
                    time: <time_1>
                    location: <location_1>
                goal_2:
                    action: <action_2>
                    time: <time_2>
                    location: <location_2>
                goal_3:
                    action: <action_3>
                    time: <time_3>
                    location: <location_3>
                ...
            }
        """
        prompt_for_plan += append_str

        ## get the result from LLM server
        try:
            response = requests.post(self.URI_PLANNING,json={'memory': prompt_for_plan})
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            if isinstance(result, str):
                result = json.loads(result) 

            # TODO: change this format to be compatible with the model's return
            plan = result['plan']
            print(f"result: {result}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling server: {e}")
            plan = "No plan can be generated from server."

        ## add to static memory so it is not decaying, overwrite the old plan
        # delete the old plan if it exists
        try:
            self.plan_memory.delete_memory(ids=[f"plan_1"])
        except: pass
        # add the new plan
        self.plan_memory.memory.add(
            documents=[str(plan)],
            metadatas=[{"timestamp": timestamp, "importance_score": 8}], # Force model to prioritize planning with high score
            ids=[f"plan_1"] # There can be only one plan per agent per day.
        )
        print(f"Plan added to static memory: {plan}")

    def query_memory(self, prompt: str, top_k: int = 5, threshold: float = 0.35):
        """
        Query the memory system for relevant context based on the input prompt. It gives priority to short-term and static memory.
        If the context is still insufficient, it falls back to long-term memory.
        
        Args:
            prompt (str): The input prompt for which context is being retrieved.
            top_k (int): The number of top documents to retrieve (default: 5).
            threshold (float): The minimum score threshold for documents to be considered relevant (default: 0.5).
        """
        
        # Priority order: Short-Term & Static -> Long-Term
        context = []
        # for memory in [self.short_term_memory, self.static_memory, self.reflection_memory, self.plan_memory]:         # FOR FUTURE USE
        for memory in [self.short_term_memory, self.static_memory]:
            results = memory.query_memory(prompt=prompt, top_k=top_k, threshold=threshold, custom_scoring=self._scoring_function)
            context.extend(results)
            if len(context) > top_k:
                break  # Stop if we have enough context

        # If context is still insufficient, fall back to long-term memory
        if len(context) < top_k:
            if(self.verbose): print("Falling back to long-term memory...")
            long_term_results = self.long_term_memory.query_memory(self.long_term_memory, prompt, top_k - len(context))
            context.extend(long_term_results)

        # Sort the context by highest score in descending order
        if context: context = sorted(context[:top_k], key=lambda x: x["score"], reverse=True)
        
        return self._format_context_output(prompt, context)
    
    def get_stats(self):
        """
        Get statistics of the memory.
        
        Args:
            memory_type (str): The type of memory to get statistics for. Can be 'static', 'short-term', 'long-term', or 'all'.
        
        Returns:
            dict: The statistics of the memory.
        """
        static_stats = self.static_memory.get_stats()
        short_term_stats = self.short_term_memory.get_stats()
        long_term_stats = self.long_term_memory.get_stats()
        plan_stats = self.plan_memory.get_stats()
        reflection_stats = self.reflection_memory.get_stats()
        return {
            "static_memory": static_stats,
            "short_term_memory": short_term_stats,
            "long_term_memory": long_term_stats,
            "plan_memory": plan_stats,
            "reflection_memory": reflection_stats
        }
        
    def reset_memory(self):
        """
        Reset all memory stores.
        """
        self.static_memory.clear_memory()
        self.short_term_memory.clear_memory()
        self.long_term_memory.clear_memory()
        self.reflection_memory.clear_memory()
        self.plan_memory.clear_memory()
        return
    
    def _scoring_function(self, similarity_score, metadata, weights = [0.5, 0.5]) -> float:
        if('importance_score' in metadata): print(metadata['importance_score'])
        return similarity_score*weights[0] + metadata['importance_score']*weights[1] if 'importance_score' in metadata else similarity_score
        
    def _calculate_recency_score(self, timestamp: str, current_time: str = None, decay_factor: float = 0.995) -> float:
        """
        Calculate the recency score using an exponential decay function.
        
        Args:
            timestamp (str): The timestamp string in ISO format of when the memory was created/last accessed
            current_time (str): The current time string in ISO format to compare against (default: current time)
            decay_factor (float): The decay factor for the exponential decay (default: 0.995)
        
        Returns:
            float: A recency score between 0 and 1, where 1 indicates most recent
        """
        if timestamp is None:
            return 1.0  # Return maximum score if no timestamp provided
            
        # Convert timestamp strings to datetime objects
        if current_time is None:
            current_time = datetime.now().isoformat()
            
        timestamp_dt = datetime.fromisoformat(timestamp)
        current_time_dt = datetime.fromisoformat(current_time)
        
        # Calculate the time difference in hours
        time_diff = current_time_dt - timestamp_dt
        hours_diff = time_diff.total_seconds() / (3600*3)
        
        # Calculate recency score using exponential decay
        recency_score = math.pow(decay_factor, hours_diff)
        
        # Ensure the score is between 0 and 1
        recency_score = max(0.0, min(1.0, recency_score))
        
        return recency_score

    def _initial_recency_and_importance_score_calculator(self,doc: str, timestamp: str, weights = [0.5, 0.5]) -> float:
        """
        Calculate the importance score of a document. 
        The parameters considered are Relevency, Recency, Frequency, Personal Impact

        Args:
            doc (str): The document text
            timestamp (str): ISO format timestamp string
        """
        recency = self._calculate_recency_score(timestamp)

        # Call the memory rating server
        try:
            response = requests.post(self.URI_RATING,json={'memory': doc})
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            if isinstance(result, str):
                result = json.loads(result) 

            personal_impact = int(result['rating'])    
        except requests.exceptions.RequestException as e:
            print(f"Error calling memory rating server: {e}")
            personal_impact = 5  # Default value if the server call fails
        except:
            personal_impact = 5

        
        importance_score = (
            recency * weights[0] + 
            personal_impact * weights[1]
        )
        
        return importance_score
 
    def _format_context_output(self, prompt: str, context: list[str], separator: str = "\n---\n") -> str:
        """
        Formats the retrieved context into a final text output with separators.

        Args:
            prompt (str): The input prompt for which context is being retrieved.
            context (List[str]): List of retrieved documents to be used as context.
            separator (str): Separator string to distinguish between context documents.

        Returns:
            str: A formatted text output containing the context for the given prompt.
        """      
        # Header for the final output
        formatted_output = f"Context for Prompt: '{prompt}'\n\n"

        # NOTE: handle in case no matched context found here
        if not context:
            formatted_output += "No important context found"
            return formatted_output

        # Add each document separated by the specified separator
        for idx, document in enumerate(context, 1):
            # formatted_output += f"[Document {idx}]:\n{document['document'], document['distances']}{separator}"
            formatted_output += f"[Document {idx}]:\n{document['document']}{separator}"

        # Remove the last separator for cleaner formatting
        formatted_output = formatted_output.rstrip(separator)

        return formatted_output       
    
    def _initiate_memory(self):
        """
        Initiates the memory system by creating the memory collections.
        """
        self.static_memory.initiate_memory(self.base_client_path+f'/{self.agent_name}', f"{self.static_memory.name}")
        self.short_term_memory.initiate_memory(self.base_client_path+f'/{self.agent_name}', f"{self.short_term_memory.name}")
        self.long_term_memory.initiate_memory(self.base_client_path+f'/{self.agent_name}', f"{self.long_term_memory.name}")
        self.reflection_memory.initiate_memory(self.base_client_path+f'/{self.agent_name}', f"{self.reflection_memory.name}")
        self.plan_memory.initiate_memory(self.base_client_path+f'/{self.agent_name}', f"{self.plan_memory.name}")
        return



