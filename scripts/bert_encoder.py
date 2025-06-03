

from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import os

class BERTEncoder:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModel.from_pretrained(model_path, local_files_only=True)
        self.model.eval()
        print("BERTEncoder loaded")

    def encode(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
        cls_vec = outputs.last_hidden_state[:, 0, :]  # [CLS] 向量
        return cls_vec.squeeze().numpy()
