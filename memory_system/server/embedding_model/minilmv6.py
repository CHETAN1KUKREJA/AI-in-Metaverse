import torch
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

class MiniLMv6Retriever:
    def __init__(self, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        try:
            self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.device = device
            # Explicitly specify max_seq_length to avoid tokenizer issues
            self.model = SentenceTransformer(
                self.model_name,
                device=device
            )
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise

    def get_text_embeddings(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: int = 32
    ) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
           
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_tensor=True,
            device=self.device,
            normalize_embeddings=normalize
        )
       
        return embeddings.cpu().numpy()

    def __call__(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        return self.get_text_embeddings(texts, **kwargs)
