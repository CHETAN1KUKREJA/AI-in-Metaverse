import torch
import torch.nn.functional as F
from torch import Tensor
from typing import List, Union, Tuple, Optional, Literal
from enum import Enum
from .baseRetriever import BaseRetriever, QuantizationConfig


class SFRMistralRetriever(BaseRetriever):
    """Enhanced SFR-Mistral Retriever with configurable quantization"""
    def __init__(
        self,
        model_name: str = "Salesforce/SFR-Embedding-Mistral",
        quantization: Optional[QuantizationConfig] = None,
        batch_size_per_gpu: int = 32,
        max_length: int = 4096
    ):
        super().__init__(model_name, quantization)
        self.devices = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
        self.batch_size_per_gpu = batch_size_per_gpu
        self.max_length = max_length
        print(f"Using {len(self.devices)} GPUs: {self.devices}")

    def _last_token_pool(
        self,
        last_hidden_states: Tensor,
        attention_mask: Tensor
    ) -> Tensor:
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[
            torch.arange(batch_size, device=last_hidden_states.device),
            sequence_lengths
        ]

    def _get_detailed_instruct(self, task_description: str, query: str) -> str:
        return f'Instruct: {task_description}\nQuery: {query}'

    def get_text_embeddings(
        self,
        texts: Union[str, List[str]],
        task_description: str = None,
        normalize: bool = True
    ) -> torch.Tensor:
        if isinstance(texts, str):
            texts = [texts]

        if task_description:
            texts = [self._get_detailed_instruct(task_description, query) 
                    for query in texts]

        total_batch_size = self.batch_size_per_gpu * len(self.devices)
        all_embeddings = []
        
        for i in range(0, len(texts), total_batch_size):
            batch_texts = texts[i:i + total_batch_size]
            batch_dict = self.tokenizer(
                batch_texts,
                max_length=self.max_length,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            batch_dict = {k: v.to(self.model.device) 
                         for k, v in batch_dict.items()}

            with torch.no_grad():
                outputs = self.model(**batch_dict)
                batch_embeddings = self._last_token_pool(
                    outputs.last_hidden_state,
                    batch_dict['attention_mask']
                )
                all_embeddings.append(batch_embeddings.cpu())

        embeddings = torch.cat(all_embeddings, dim=0)
        
        if normalize:
            embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings