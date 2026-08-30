"""Train a CODE122 model from random initialization.
Usage: python train.py --role code --data data.txt --steps 1000
"""
import argparse, json, os
import torch
from transformer import Config, RoboTransformer

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--role',required=True); ap.add_argument('--data',required=True); ap.add_argument('--steps',type=int,default=1000); ap.add_argument('--out',default='checkpoints'); a=ap.parse_args()
    with open(a.data,'r',encoding='utf8') as f: text=f.read()
    chars=sorted(set(text)); stoi={c:i for i,c in enumerate(chars)}; ids=torch.tensor([stoi[c] for c in text],dtype=torch.long)
    if len(ids)<2: raise SystemExit('training data is too small')
    c=Config(vocab_size=len(chars),max_seq_len=min(512,max(32,len(ids)-1)),d_model=384,n_heads=6,n_layers=6)
    model=RoboTransformer(c); opt=torch.optim.AdamW(model.parameters(),lr=3e-4,weight_decay=0.1); model.train()
    for step in range(a.steps):
        n=min(c.max_seq_len,len(ids)-1); start=torch.randint(0,len(ids)-n,(1,)).item(); x=ids[start:start+n][None,:]; y=ids[start+1:start+n+1][None,:]
        _,loss=model(x,y); opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        if step%100==0: print(f'{a.role} step={step} loss={loss.item():.4f}')
    os.makedirs(a.out,exist_ok=True); path=os.path.join(a.out,a.role+'.pt'); torch.save({'role':a.role,'config':c.__dict__,'vocab':chars,'state_dict':model.state_dict(),'steps':a.steps},path)
    print('CHECKPOINT_WRITTEN',path)
if __name__=='__main__': main()
