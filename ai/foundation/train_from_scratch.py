"""Train one or all 48 RoboLab LMs from random initialization.
This script performs genuine next-token gradient training when torch and data are available.
It never downloads pretrained weights or calls a remote AI provider.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import torch
from torch.optim import AdamW
from .transformer import RoboLabTransformer, ModelConfig
from ai.local_models.registry import MODEL_SPECS

SPECIALIST_TEXT = Path("ai/datasets/specialist_corpus.jsonl")

def load_tokens(path, vocab_size, seq_len):
    rows=[]
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try: rows.append(json.loads(line).get("text", ""))
            except json.JSONDecodeError: pass
    if not rows: raise RuntimeError("No training corpus. Add licensed/owned text to ai/datasets/specialist_corpus.jsonl; no web corpus is fetched.")
    vocab={"<unk>":0}; ids=[]
    for text in rows:
        toks=text.lower().split()
        seq=[]
        for tok in toks:
            if tok not in vocab and len(vocab)<vocab_size: vocab[tok]=len(vocab)
            seq.append(vocab.get(tok,0))
        ids.extend(seq)
    if len(ids)<seq_len+1: raise RuntimeError("Training corpus is too small for configured sequence length.")
    return torch.tensor(ids,dtype=torch.long), vocab

def train(role, steps, device):
    c=ModelConfig(); model=RoboLabTransformer(c).to(device)
    ids,vocab=load_tokens(SPECIALIST_TEXT,c.vocab_size,c.max_seq_len)
    opt=AdamW(model.parameters(),lr=3e-4,weight_decay=0.1)
    model.train(); losses=[]
    for step in range(steps):
        start=(step*c.max_seq_len)%(len(ids)-c.max_seq_len-1)
        x=ids[start:start+c.max_seq_len].unsqueeze(0).to(device)
        y=ids[start+1:start+c.max_seq_len+1].unsqueeze(0).to(device)
        out=model(x,y); out["loss"].backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); opt.zero_grad(set_to_none=True)
        losses.append(float(out["loss"].detach().cpu()))
    out=Path("ai/checkpoints/neural")/role; out.mkdir(parents=True,exist_ok=True)
    torch.save({"role":role,"model_state_dict":model.state_dict(),"config":c.__dict__,"vocab":vocab,"steps":steps,"from_scratch":True,"final_loss":losses[-1]},out/"model.pt")
    return losses[-1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--role",default="all",choices=["all",*MODEL_SPECS]); ap.add_argument("--steps",type=int,default=100); ap.add_argument("--device",default="cuda" if torch.cuda.is_available() else "cpu"); a=ap.parse_args()
    roles=list(MODEL_SPECS) if a.role=="all" else [a.role]
    print(f"training {len(roles)} model(s) from random initialization on {a.device}; no pretrained weights")
    for role in roles: print(role, train(role,a.steps,a.device))
if __name__=="__main__": main()
