# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 07:46:16 2024

@author: Arun Joshi
"""
from torch import nn
import math
# import numpy as np
import torch
from .tokenizer import Tokenizer

class InputEmbedding(nn.Module):
    def __init__(self, d_model: int, vocab_size: int, padding_idx: int) -> None:
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.padding_idx = padding_idx
        self.embedding_layer = nn.Embedding(
            self.vocab_size, self.d_model, self.padding_idx)

    def forward(self, x):
        input_embedding = self.embedding_layer(x)
        return input_embedding * math.sqrt(self.d_model)
    '''Following the attention is all you need paper for the implemention of 
        math.sqrt(d_model) in the input_embedding. 
        Link for the page is  : https://arxiv.org/pdf/1706.03762 -> Page no 5.'''


'''
class PostionalEncoding(nn.Module):
    def __init__(self, seq_len:int, d_model:int, dropout:float = 0.1 ,n:int = 10000):
        super().__init__()
        self.dropout = dropout
        self.d_model = d_model
        self.seq_len = seq_len
        self.n = n
        self.dropout_layer = nn.Dropout(self.dropout)
        
    
    def forward(self,x):
        P = np.zeros((self.seq_len, self.d_model))
        for k in range(self.seq_len):
            for i in np.arange(int(self.d_model/2)):
                denominator = np.power(self.n, 2*i/self.d_model)
                P[k, 2*i] = np.sin(k/denominator)
                P[k, 2*i+1] = np.cos(k/denominator)
        P = torch.from_numpy(P)
        P = P.expand(x.shape(0), self.seq_len, self.d_model)
        x = x + P
        return self.dropout(x)
'''


class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, max_len: int, dropout: float = 0.1, ):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)  # -> (max_len,1)
        div_term = torch.exp(torch.arange(0, d_model, 2)
                             * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)  # -> (max_len,1,d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    def __init__(self, h: int, d_model: int, dropout:float = 0.1):
        super().__init__()
        self.h = h
        self.d_model = d_model
        self.d_k = d_model // h
        assert d_model % h == 0, 'Make sure d_model is divisible by h'
        self.linear_layer1 = nn.Linear(d_model, d_model, bias=False)
        self.linear_layer2 = nn.Linear(d_model, d_model, bias=False)
        self.linear_layer3 = nn.Linear(d_model, d_model, bias=False)
        self.linear_layer4 = nn.Linear(d_model, d_model, bias=False)
        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, q, k, v, src_mask):
        query = self.linear_layer1(q)  # (Batch, seq_len, d_model)
        key = self.linear_layer2(k)  # (Batch, seq_len, d_model)
        value = self.linear_layer3(v)  # (Batch, seq_len, d_model)

        # We need to reshape the q, k,v tensors in the shape (Batch, h, seq_len, d_k) first
        # Since d_k * h == d_model, we can reshape our tensor as (Batch, seq_len, h, d_k) and rearragne the dimensions
        query = query.view(
            query.shape[0], query.shape[1], self.h, self.d_k).transpose(1, 2)
        key = key.view(value.shape[0], key.shape[1],
                       self.h, self.d_k).transpose(1, 2)
        value = value.view(
            value.shape[0], value.shape[1], self.h, self.d_k).transpose(1, 2)

        x = self.attention_block(query, key, value, src_mask, self.dropout_layer)
        x = x.transpose(1, 2).contiguous().view(
            x.shape[0], -1, self.h * self.d_k)

        return self.linear_layer4(x)

    def attention_block(self, query, key, value, mask, dropout:nn.Dropout):
        # the masking will also be of shape (batch,h,seq_len,seq_len)
        attention_scores = torch.matmul(
            query, key.transpose(-2, -1))/math.sqrt(self.d_k)
        # Attention_scores will be of (batch_size, h, seq_len,seq_len) -> (1,4,100,100)
        if mask is not None:
            attention_scores.masked_fill(mask == 0, -1e-9)
        
        attention_scores = torch.softmax(attention_scores, dim=-1)
        if dropout is not None:
            attention_scores = dropout(attention_scores)
        return attention_scores @ value  # -> (1, head, seq_len, d_k)


class LayerNorm(nn.Module):
    def __init__(self, eps: int = 1e-05):
        super().__init__()
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1))

    def forward(self, x):
        mean = torch.mean(x, dim=-1, keepdim=True)  # -> (Batch, seq_len, 1)
        var = torch.var(x, dim=-1, keepdim=True)

        x = ((x - mean) * self.gamma)/torch.sqrt(var + self.eps) + self.beta
        return x


class ResidualConnection(nn.Module):
    def __init__(self, dropout:float = 0.1):
        super().__init__()
        self.norm = LayerNorm()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        return self.norm(x + self.dropout(sublayer(x)))
        


class FeedForwardNet(nn.Module):
    def __init__(self, d_model:int, d_ff : int, dropout:float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.linear_layer1 = nn.Linear(d_model, d_ff)
        self.linear_layer2 = nn.Linear(d_ff,d_model)
        self.relu = nn.ReLU()
        self.dropout_layer = nn.Dropout(dropout)

    def forward(self,x):
        return self.linear_layer2(
            self.dropout_layer(self.relu(self.linear_layer1(x))))


class ProjectionLayer(nn.Module):
    def __init__(self, d_model:int, unique_labels: int):
        super().__init__()
        self.d_model = d_model
        self.unique_labels = unique_labels
        self.linear_layer = nn.Linear(d_model, unique_labels)
        #self.softmax_layer = nn.Softmax(dim = -1)
        

    def forward(self,x):
        pooled_output = torch.mean(x, dim=1)  # Averaging over seq_len
        #return self.softmax_layer(self.linear_layer(pooled_output))
        return self.linear_layer(pooled_output)
    
    
class EncoderBlock(nn.Module):
    def __init__(self, attention_block: MultiHeadAttention, 
                 feed_forward_block: FeedForwardNet, dropout:float = 0.1):
        super().__init__()
        self.attention_block = attention_block
        self.feed_forward_block = feed_forward_block
        self.residual_layer = nn.ModuleList([ResidualConnection() for _ in range(2)])
    def forward(self,x, src_mask):
        x = self.residual_layer[0](
            x, lambda x: self.attention_block(x,x,x,src_mask))
        x = self.residual_layer[1](
            x,self.feed_forward_block)
        return x
    
class Encoders(nn.Module):
    def __init__(self, ):
        pass
    def forward(self):
        pass
    

#encoder : Encoder(MultiHeadAttention(), FeedForwardNet())

class SentimentModel(nn.Module):
    def __init__(self, h:int, d_model:int,d_ff:int,unique_labels:int):
        super().__init__()
        self.tokenizer = Tokenizer()
        self.input_embed_layer = InputEmbedding(d_model,self.tokenizer.get_vocabsize(),0)
        self.positional_layer = PositionalEncoding(d_model,100)
        self.encoder = EncoderBlock(MultiHeadAttention(h, d_model), 
                                    FeedForwardNet(d_model, d_ff))
        self.proj_layer = ProjectionLayer(d_model, unique_labels)
        #self.input_embeddings = input_embeddings
        #self.input_mask = input_mask
    def forward(self,x, mask): #x here should me the tokenized input id from dataloaders
        x = self.input_embed_layer(x.transpose(-1,-2))
        x = self.positional_layer(x.squeeze(dim = -2)
                                             )
        encoder_output = self.encoder(x, mask)
        final_output = self.proj_layer(encoder_output)
        return final_output