import torch
from transformers import AutoTokenizer, AutoModel, BitsAndBytesConfig
from typing import List, Union, Tuple, Optional, Literal
from sklearn.metrics.pairwise import euclidean_distances
from dataclasses import dataclass
from enum import Enum

class QuantizationType(Enum):
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    INT4_NESTED = "int4_nested"
    FP16 = "fp16"

@dataclass
class QuantizationConfig:
    quant_type: QuantizationType = QuantizationType.NONE
    compute_dtype: torch.dtype = torch.float32
    double_quant: bool = False
    quant_scheme: Literal["nf4", "fp4"] = "nf4"

class BaseRetriever:
    """Base class for retrieval models with configurable quantization"""
    def __init__(
        self,
        model_name: str,
        quantization: Optional[QuantizationConfig] = None,
        device_map: str = "auto"
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Ensure tokenizer has padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if quantization is None:
            quantization = QuantizationConfig()
        
        # Configure model loading based on quantization type
        model_kwargs = {"device_map": device_map}
        
        if quantization.quant_type != QuantizationType.NONE:
            if quantization.quant_type == QuantizationType.FP16:
                model_kwargs["torch_dtype"] = torch.float16
            else:
                bnb_config = BitsAndBytesConfig(
                    load_in_8bit=(quantization.quant_type == QuantizationType.INT8),
                    load_in_4bit=(quantization.quant_type in 
                                 [QuantizationType.INT4, QuantizationType.INT4_NESTED]),
                    bnb_4bit_compute_dtype=quantization.compute_dtype,
                    bnb_4bit_use_double_quant=(quantization.quant_type == 
                                              QuantizationType.INT4_NESTED),
                    bnb_4bit_quant_type=quantization.quant_scheme
                )
                model_kwargs["quantization_config"] = bnb_config
        
        self.model = AutoModel.from_pretrained(model_name, **model_kwargs)
        
    def _compute_similarity(
        self,
        query_embedding: torch.Tensor,
        text_embeddings: torch.Tensor,
        k: int,
        similarity_metric: str,
        texts: List[str]
    ) -> Tuple[List[str], List[float]]:
        """Compute similarities and return top-k results"""
        if similarity_metric == "cosine":
            similarities = (query_embedding @ text_embeddings.t()).squeeze() * 100
            top_k = torch.topk(similarities, min(k, len(texts)))
            scores = top_k.values.tolist()
        elif similarity_metric == "euclidean":
            distances = euclidean_distances(
                query_embedding.numpy(),
                text_embeddings.numpy()
            ).squeeze()
            top_k = torch.topk(torch.from_numpy(-distances), min(k, len(texts)))
            scores = [-x for x in top_k.values.tolist()]
        
        results = [texts[idx] for idx in top_k.indices]
        return results, scores
