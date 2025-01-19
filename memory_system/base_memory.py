from abc import ABC, abstractmethod
import chromadb
import json
import os
from chromadb import Collection
import numpy as np
from datetime import datetime

class BaseMemory(ABC):
    """
    Abstract Base Class for all memory types.
    Provides a standard interface for memory management operations.
    """

    required_methods = ["initiate_memory", "add", "query_memory", "delete_memory", "clear_memory"]

    def __init__(self, name="BaseMemory", verbose=True):
        """
        Initialize the memory with a name.
        
        :param name: Name of the memory system (useful for logging and debugging)
        """
        self.name = name
        self.verbose = verbose
        self._assert_methods_implemented()

    def _assert_methods_implemented(self):
        """
        Ensure that all abstract methods are implemented in the subclass.
        Raises an AssertionError if any required method is missing.
        """
        for method_name in self.required_methods:
            if not callable(getattr(self, method_name, None)):
                raise NotImplementedError(
                    f"Class '{self.__class__.__name__}' must implement the method '{method_name}'."
                )

    @abstractmethod
    def initiate_memory(self):
        """
        Abstract method to initialize the memory.
        Should be implemented in subclasses to define how memory is set up.
        """
        pass

    @abstractmethod
    def add(self, key, value):
        """
        Abstract method to add a key-value pair to the memory.
        
        :param key: Identifier for the memory item
        :param value: Data associated with the key
        """
        pass

    @abstractmethod
    def query_memory(self, key):
        """
        Abstract method to retrieve a value from the memory.
        
        :param key: Identifier for the memory item to be queried
        :return: Data associated with the key or an appropriate message if not found
        """
        pass

    @abstractmethod
    def delete_memory(self, key):
        """
        Abstract method to delete a specific item from the memory.
        
        :param key: Identifier for the memory item to be deleted
        """
        pass

    @abstractmethod
    def clear_memory(self):
        """
        Abstract method to clear all data from the memory.
        """
        pass

    def describe(self):
        """
        Optional utility method to describe the memory system.
        This can be overridden in subclasses to provide specific details.
        """
        return f"This is the {self.name} system. It's used to manage memory effectively."

    def __repr__(self):
        """
        Return a string representation of the memory system.
        """
        return f"<{self.__class__.__name__}(name='{self.name}')>"

from dataclasses import dataclass

@dataclass
class MemoryEntry:
    documents: list[str]
    metadatas: list[dict]
    ids: list[str]

class ChromaMemory(BaseMemory):
    def __init__(self, name="ChromaMemory", verbose=True, description=""):
        super().__init__(name, verbose)
        self.description = "This is a simple memory system that stores data in a list." if description == "" else description
        return
    
    def initiate_memory(self, client_path, collection_name):
        self.client = chromadb.PersistentClient(client_path)
        self.memory: Collection = self.client.get_or_create_collection(collection_name)
        return
        
    def add(self, input_data, overwrite_existing=False):
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
            if "timestamp" not in meta:
                meta["timestamp"] = str(datetime.now().isoformat())

        existing_ids = set(self.memory.get()["ids"])
        new_documents = []
        new_metadatas = []
        new_ids = []

        for doc, meta, id_ in zip(documents, metadatas, ids):
            if id_ in existing_ids:
                if overwrite_existing:
                    self.memory.delete(ids=[id_])
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
            self.memory.add(
                documents=new_documents,
                metadatas=new_metadatas,
                ids=new_ids,
            )
            print(f"Added {len(new_ids)} static memories successfully.")
        else:
            print("No new memories added.")

        return
    
    
    def query_memory(self, prompt:str, top_k:int = 1, threshold=None, custom_scoring = None) -> dict:
        try:
            results = self.memory.query(
                query_texts=[prompt],
                n_results=self.memory.count(),
                include=["metadatas", "distances"]
            )
        except:
            return []
        
        # Now, calculate the similarity and total score
        similarities = [1/(1+dist) for dist in results["distances"][0]]
        # If the similarities are None, that means the query returns no results -> return empty context
        if not similarities:
            return {}
        
        if custom_scoring:
            scores = np.array([custom_scoring(sim, meta) for meta, sim in zip(results["metadatas"][0], similarities)])
        
        # Sort the scores in descending order, get the top k ids
        top_k_indices = np.argsort(scores)[::-1][:top_k].astype(int)
        top_k_ids = [results["ids"][0][i] for i in top_k_indices]
        if(self.verbose): print(f"top_k_ids: {top_k_ids}")

        final_results = self.memory.get(
            ids=top_k_ids,
            include=["documents", "metadatas"]
        )

        documents = final_results["documents"] # list of string already
        metadatas = final_results["metadatas"] # list of json strings
        final_scores = scores[top_k_indices]
        distances = np.array(results["distances"][0])[top_k_indices]
        
        context_local = []
        for doc, meta, dist, score in zip(documents, metadatas, distances, final_scores):
            if score >= threshold:
                context_local.append(
                    {
                        "document": doc, 
                        "metadata": meta, 
                        "distances": dist,
                        "score": score
                    }
                )
        return context_local

    def delete_memory(self, keys):
        """
        Deletes a memory from the memory system.
        
        :param key: Identifier for the memory item to be deleted as a list
        """
        try: self.memory.delete(ids=keys)
        except: pass   # Key not found
        return
                    
    def clear_memory(self):
        try: self.memory.delete(ids=self.memory.get()["ids"])
        except: pass    # Memory is already empty
        return

    def describe(self):
        return self.description

    def get_stats(self):
        return {
            "memory_size": self.memory.count(),
            "memory_ids": self.memory.get()["ids"]
        }
        
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', memory={self.memory})>"
   
if __name__ == "__main__":
    a = ChromaMemory()
    print(type(a))