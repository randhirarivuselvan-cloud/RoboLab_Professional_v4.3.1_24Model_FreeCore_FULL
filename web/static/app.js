async function enterApp(){
  document.getElementById('auth').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
  await loadRegion(); await loadCopilotStatus();
}
async function loadRegion(){
  try{const r=await fetch('/api/location'); const d=await r.json(); document.getElementById('region').textContent=`🌐 ${d.country} · IP region`;}
  catch(e){document.getElementById('region').textContent='🌐 Region unavailable';}
}
async function loadCopilotStatus(){
  try{const r=await fetch('/api/copilot/status'); const d=await r.json(); document.getElementById('copilot-status').textContent=d.available?`● ${d.provider}`:'● baseline';}
  catch(e){document.getElementById('copilot-status').textContent='offline';}
}
function showHome(){window.scrollTo({top:0,behavior:'smooth'})}
async function analyze(){
  const description=document.getElementById('idea').value.trim();
  if(!description){alert('Describe your idea first.');return}
  const r=await fetch('/api/idea/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({description})});
  const d=await r.json();
  const result=document.getElementById('result'); result.classList.remove('hidden');
  result.innerHTML=`<h3>✨ Concept captured</h3><p>${escapeHtml(d.concept)}</p><h4>Architecture</h4><pre>${escapeHtml(JSON.stringify(d.architecture,null,2))}</pre><h4>Next steps</h4><p>${(d.next_steps||[]).map(escapeHtml).join('\n')}</p><p><b>${escapeHtml(d.status||'Ready')}</b></p>`;
  result.scrollIntoView({behavior:'smooth'});
}
async function runStage(stage){
  const description=document.getElementById('idea').value.trim(); if(!description){alert('Describe your idea first.');return}
  const r=await fetch(`/api/ai/${stage}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({description,idea:description,project:{description}})});
  const d=await r.json();
  const result=document.getElementById('result'); result.classList.remove('hidden');
  result.innerHTML=`<h3>${escapeHtml(stage)}</h3><pre>${escapeHtml(JSON.stringify(d,null,2))}</pre>`; result.scrollIntoView({behavior:'smooth'});
}
async function copilotAsk(action){
  const message=document.getElementById('copilot-input').value.trim(); if(!message){return}
  const context={idea:document.getElementById('idea').value.trim()};
  const box=document.getElementById('copilot-result'); box.textContent='Thinking…';
  const r=await fetch('/api/copilot/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,action,context})});
  const d=await r.json();
  box.innerHTML=`<pre>${escapeHtml(JSON.stringify(d,null,2))}</pre>`;
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}
