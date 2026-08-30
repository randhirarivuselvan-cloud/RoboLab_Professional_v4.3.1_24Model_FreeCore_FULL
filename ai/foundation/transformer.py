from __future__ import annotations
from dataclasses import dataclass
import torch
from torch import nn

@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 32768
    max_seq_len: int = 2048
    d_model: int = 768
    n_heads: int = 12
    n_layers: int = 12
    ffn_mult: int = 4
    dropout: float = 0.0

class CausalSelfAttention(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.qkv = nn.Linear(c.d_model, 3*c.d_model, bias=False)
        self.out = nn.Linear(c.d_model, c.d_model, bias=False)
        self.n_heads = c.n_heads
        self.head_dim = c.d_model // c.n_heads
        self.register_buffer("mask", torch.tril(torch.ones(c.max_seq_len, c.max_seq_len, dtype=torch.bool)), persistent=False)
    def forward(self, x):
        b,t,d=x.shape
        q,k,v=self.qkv(x).chunk(3,dim=-1)
        q=q.view(b,t,self.n_heads,self.head_dim).transpose(1,2)
        k=k.view(b,t,self.n_heads,self.head_dim).transpose(1,2)
        v=v.view(b,t,self.n_heads,self.head_dim).transpose(1,2)
        y=nn.functional.scaled_dot_product_attention(q,k,v,is_causal=True)
        return self.out(y.transpose(1,2).contiguous().view(b,t,d))

class Block(nn.Module):
    def __init__(self,c):
        super().__init__()
        self.n1=nn.LayerNorm(c.d_model)
        self.attn=CausalSelfAttention(c)
        self.n2=nn.LayerNorm(c.d_model)
        self.ff=nn.Sequential(nn.Linear(c.d_model,c.ffn_mult*c.d_model),nn.GELU(),nn.Linear(c.ffn_mult*c.d_model,c.d_model))
    def forward(self,x):
        x=x+self.attn(self.n1(x))
        return x+self.ff(self.n2(x))

class RoboLabTransformer(nn.Module):
    """Decoder-only causal LM with random initialization; no pretrained weights."""
    def __init__(self,c:ModelConfig):
        super().__init__(); self.config=c
        self.tok=nn.Embedding(c.vocab_size,c.d_model)
        self.pos=nn.Embedding(c.max_seq_len,c.d_model)
        self.blocks=nn.ModuleList([Block(c) for _ in range(c.n_layers)])
        self.norm=nn.LayerNorm(c.d_model); self.lm_head=nn.Linear(c.d_model,c.vocab_size,bias=False)
        self.lm_head.weight=self.tok.weight
        self.apply(self._init)
    @staticmethod
    def _init(m):
        if isinstance(m,nn.Linear): nn.init.normal_(m.weight,mean=0.0,std=0.02)
        elif isinstance(m,nn.Embedding): nn.init.normal_(m.weight,mean=0.0,std=0.02)
    def forward(self,input_ids,labels=None):
        b,t=input_ids.shape
        if t>self.config.max_seq_len: raise ValueError("sequence exceeds max_seq_len")
        p=torch.arange(t,device=input_ids.device)
        x=self.tok(input_ids)+self.pos(p)[None,:,:]
        for block in self.blocks: x=block(x)
        logits=self.lm_head(self.norm(x))
        loss=None
        if labels is not None: loss=nn.functional.cross_entropy(logits.view(-1,logits.size(-1)),labels.view(-1),ignore_index=-100)
        return {"logits":logits,"loss":loss}
