# -*- coding: utf-8 -*-
# Load model directly
from transformers import AutoTokenizer


class Tokenizer():
    def __init__(self, return_tensors='pt'):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "google-bert/bert-base-uncased")
        self.return_tensors = return_tensors

    def tokenize(self, input_text, max_length: int):
        input_token = self.tokenizer(
            input_text, padding='max_length',
            truncation=True, max_length= max_length,
            return_tensors=self.return_tensors, 
        )
        return input_token
    
    def get_vocabsize(self):
        return self.tokenizer.vocab_size
