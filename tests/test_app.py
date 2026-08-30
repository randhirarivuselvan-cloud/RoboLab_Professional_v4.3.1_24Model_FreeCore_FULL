from fastapi.testclient import TestClient
from main import app
client=TestClient(app)

def test_status_and_health():
    assert client.get('/api/status').status_code==200
    assert client.get('/health').json()['status']=='online'

def test_frontend():
    r=client.get('/'); assert r.status_code==200; assert 'RoboLab' in r.text

def test_native_provider():
    r=client.get('/api/ai/providers'); assert r.status_code==200; assert r.json()['provider']=='none'; assert r.json()['available'] is False

def test_ai_endpoints_without_external_key():
    for stage in ['architect','circuit','cad','verify','audit','bom']:
        r=client.post(f'/api/ai/{stage}',json={'description':'Arduino rover with ultrasonic sensor and motor driver'})
        assert r.status_code==200, (stage,r.text)
    r=client.post('/api/ai/code',json={'description':'Arduino rover with motor and ultrasonic sensor'})
    assert r.status_code==200 and 'code' in r.json()['result']

def test_consensus():
    r=client.post('/api/ai/consensus',json={'project':{'stages':{}}}); assert r.status_code==200

def test_copilot_and_specialist_endpoints():
    assert client.get('/api/ai/models').status_code == 200
    assert client.get('/api/copilot/status').status_code == 200
    r=client.post('/api/copilot/chat',json={'message':'How should I test a motor controller?','action':'test','context':{'idea':'rover'}})
    assert r.status_code==200
    for stage in ['component','simulation','documentation','verifier_1','verifier_2','compiler_1','compiler_2']:
        r=client.post(f'/api/ai/{stage}',json={'description':'Arduino rover','project':{'stages':{}}})
        assert r.status_code==200,(stage,r.text)
