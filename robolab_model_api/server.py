from __future__ import annotations
import os, time, uuid
from typing import Any
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from ai.model_registry import MODEL_SPECS, model_for

APP_NAME='RoboLab Custom Model Gateway'
API_KEY=os.getenv('ROBO_MODEL_API_KEY','')
DEFAULT_MODEL=os.getenv('ROBO_MODEL_ID','robolab-code')
MAX_NEW_TOKENS=int(os.getenv('ROBO_MAX_NEW_TOKENS','2048'))
DEFAULT_TEMPERATURE=float(os.getenv('ROBO_TEMPERATURE','0.15'))
app=FastAPI(title=APP_NAME,version='2.0.0')
_model_cache: dict[str, tuple[Any,Any]]={}
_load_errors: dict[str,str]={}


def _auth(authorization: str|None=Header(default=None)) -> None:
    if not API_KEY: return
    if not authorization or not authorization.startswith('Bearer ') or authorization[7:].strip()!=API_KEY:
        raise HTTPException(status_code=401,detail='Invalid or missing bearer token')


def _path_for(model_id: str) -> str:
    model_key = model_id.upper().replace('-', '_')
    direct = os.getenv('ROBO_MODEL_PATH_' + model_key)
    if direct:
        return direct
    for role, spec in MODEL_SPECS.items():
        if model_for(role) == model_id:
            role_path = os.getenv('ROBO_MODEL_PATH_' + role.upper())
            if role_path:
                return role_path
    return os.getenv('ROBO_MODEL_PATH','')


def _load_model(model_id: str):
    if model_id in _model_cache: return _model_cache[model_id]
    path=_path_for(model_id)
    if not path:
        _load_errors[model_id]='No model path configured for this model'
        return None
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok=AutoTokenizer.from_pretrained(path,use_fast=True)
        mdl=AutoModelForCausalLM.from_pretrained(path,device_map='auto',torch_dtype='auto')
        _model_cache[model_id]=(mdl,tok)
        _load_errors.pop(model_id,None)
        return mdl,tok
    except Exception as exc:
        _load_errors[model_id]=str(exc)
        return None


def _generate(model_id: str, system: str, prompt: str, max_tokens: int, temperature: float) -> str:
    pair=_load_model(model_id)
    if not pair:
        raise HTTPException(status_code=503,detail={'code':'MODEL_NOT_READY','model':model_id,'message':_load_errors.get(model_id,'Model failed to load')})
    mdl,tok=pair
    msgs=[{'role':'system','content':system},{'role':'user','content':prompt}]
    inputs=tok.apply_chat_template(msgs,add_generation_prompt=True,return_tensors='pt').to(mdl.device)
    do_sample=temperature>0
    output=mdl.generate(inputs,max_new_tokens=max_tokens,temperature=max(temperature,1e-4) if do_sample else None,do_sample=do_sample,pad_token_id=tok.eos_token_id)
    return tok.decode(output[0][inputs.shape[-1]:],skip_special_tokens=True).strip()

class GenerateRequest(BaseModel):
    model: str|None=None
    role: str|None=None
    system: str='You are RoboLab, a careful robotics engineering AI.'
    prompt: str=Field(min_length=1,max_length=100000)
    max_tokens: int=Field(default=MAX_NEW_TOKENS,ge=1,le=16384)
    temperature: float=Field(default=DEFAULT_TEMPERATURE,ge=0,le=2)

class ChatMessage(BaseModel):
    role: str=Field(pattern='^(system|user|assistant)$')
    content: str=Field(min_length=1,max_length=100000)

class ChatRequest(BaseModel):
    model: str|None=None
    role: str|None=None
    messages: list[ChatMessage]=Field(min_length=1,max_length=50)
    max_tokens: int=Field(default=MAX_NEW_TOKENS,ge=1,le=16384)
    temperature: float=Field(default=DEFAULT_TEMPERATURE,ge=0,le=2)


def resolve_model(model: str|None, role: str|None) -> str:
    if role in MODEL_SPECS: return model_for(role)
    return model or DEFAULT_MODEL

@app.get('/health')
def health(_:None=Depends(_auth)):
    configured=sum(bool(_path_for(model_for(role))) for role in MODEL_SPECS)
    return {'status':'ok','service':APP_NAME,'models':len(MODEL_SPECS),'models_configured':configured}

@app.get('/v1/models')
def models(_:None=Depends(_auth)):
    return {'object':'list','data':[{'id':model_for(role),'object':'model','owned_by':'robolab','role':role} for role in MODEL_SPECS]}

@app.post('/generate')
def generate(req:GenerateRequest,_:None=Depends(_auth)):
    model=resolve_model(req.model,req.role)
    text=_generate(model,req.system,req.prompt,req.max_tokens,req.temperature)
    return {'status':'passed','provider':'robolab','model':model,'role':req.role,'data':{'text':text}}

@app.post('/v1/chat/completions')
def chat(req:ChatRequest,_:None=Depends(_auth)):
    model=resolve_model(req.model,req.role)
    system='\n'.join(m.content for m in req.messages if m.role=='system')
    prompt='\n'.join(f'{m.role.upper()}: {m.content}' for m in req.messages if m.role!='system')
    text=_generate(model,system or 'You are RoboLab.',prompt,req.max_tokens,req.temperature)
    return {'id':f'chatcmpl-{uuid.uuid4().hex}','object':'chat.completion','created':int(time.time()),'model':model,'choices':[{'index':0,'message':{'role':'assistant','content':text},'finish_reason':'stop'}]}
