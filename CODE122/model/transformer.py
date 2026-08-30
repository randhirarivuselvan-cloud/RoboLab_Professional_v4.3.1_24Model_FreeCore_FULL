"""Small, dependency-light, randomly initialized causal Transformer for CODE122 research.
Not a pretrained or frontier model. Training is real when this module is executed on data.
"""
from dataclasses import dataclass
import math
import torch
from torch import nn

@dataclass
class Config:
    vocab_size: int = 32000
    max_seq_len: int = 512
    d_model: int = 384
    n_heads: int = 6
    n_layers: int = 6
    dropout: float = 0.0

class Block(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(c.d_model)
        self.attn = nn.MultiheadAttention(c.d_model, c.n_heads, dropout=c.dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(c.d_model)
        self.mlp = nn.Sequential(nn.Linear(c.d_model, 4*c.d_model), nn.GELU(), nn.Linear(4*c.d_model, c.d_model))
    def forward(self, x):
        n = x.size(1)
        mask = torch.full((n,n), float('-inf'), device=x.device).triu(1)
        y = self.ln1(x)
        a,_ = self.attn(y,y,y,attn_mask=mask,need_weights=False)
        x = x + a
        return x + self.mlp(self.ln2(x))

class RoboTransformer(nn.Module):
    def __init__(self, c: Config):
        super().__init__(); self.config=c
        self.tok=nn.Embedding(c.vocab_size,c.d_model); self.pos=nn.Embedding(c.max_seq_len,c.d_model)
        self.blocks=nn.ModuleList([Block(c) for _ in range(c.n_layers)])
        self.ln=nn.LayerNorm(c.d_model); self.lm=nn.Linear(c.d_model,c.vocab_size,bias=False)
        self.lm.weight=self.tok.weight
        self.apply(self._init)
    @staticmethod
    def _init(m):
        if isinstance(m,nn.Linear): nn.init.normal_(m.weight,0,0.02); nn.init.zeros_(m.bias) if m.bias is not None else None
        elif isinstance(m,nn.Embedding): nn.init.normal_(m.weight,0,0.02)
    def forward(self, ids, labels=None):
        b,t=ids.shape
        if t>self.config.max_seq_len: raise ValueError('sequence exceeds max_seq_len')
        p=torch.arange(t,device=ids.device)
        x=self.tok(ids)+self.pos(p)[None,:,:]
        for block in self.blocks: x=block(x)
        logits=self.lm(self.ln(x)); loss=None
        if labels is not None: loss=nn.functional.cross_entropy(logits.reshape(-1,logits.size(-1)),labels.reshape(-1),ignore_index=-100)
        return logits,loss
