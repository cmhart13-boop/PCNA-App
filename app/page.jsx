'use client';

import { useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';

const logo = 'https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/IMG_2337.webp';
const hero = 'https://assets.pcna.com/image/upload/ar_16:7,c_fill,g_north,pg_1,q_auto,f_jpg/Mkt_Dept/2026%20Jobs/2026-0817_Web_Messaging/0817_Web_PCNA_Hero_m.jpg';

function Nav({ page }) {
  const items = [['home','⌂','Home'],['spec','✓','Specs'],['search','⌕','Products'],['virtual','◇','Virtuals'],['quote','$','Quotes']];
  return <nav className="nav">{items.map(([id,icon,label])=><a key={id} className={page===id?'active':''} href={`/?page=${id}`}><b>{icon}</b><span>{label}</span></a>)}</nav>;
}

function Home(){
  const cards=[
    ['spec','✓','Spec Sample Order','Tell Nova what you need and build the verified PCNA order.'],
    ['virtual','◇','Virtuals / Designs','Build product, kit or packaging requests and keep the details together.'],
    ['quote','$','Quote Request','Quote a verified PCNA product at the requested quantity.'],
    ['projects','□','Projects','Keep saved customer project notes and requests in one place.']
  ];
  return <><div className="head"><a href="https://www.pcna.com/en-us"><img className="logo" src={logo} alt="PCNA"/></a></div><div className="hero"><img src={hero} alt="PCNA lifestyle"/></div><div className="sectionTitle">What do you need?</div><div className="grid">{cards.map(([id,icon,title,copy])=><a className="card" href={`/?page=${id}`} key={id}><div className="icon">{icon}</div><h3>{title}</h3><p>{copy}</p><div className="arrow">→</div></a>)}</div></>;
}

async function pcna(params){
  const qs=new URLSearchParams(params);
  const r=await fetch(`/api/pcna?${qs.toString()}`);
  const data=await r.json();
  if(!r.ok) throw new Error(data.detail||data.error||'Request failed');
  return data;
}

function SearchTool(){
  const [q,setQ]=useState(''); const [rows,setRows]=useState([]); const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  const go=async()=>{setBusy(true);setError('');try{const d=await pcna({action:'search',q});setRows(d.results||[])}catch(e){setError(e.message)}finally{setBusy(false)}};
  return <Tool title="Product Search" copy="Search the verified PCNA starter catalog by product name or item number."><label>Product name or item number</label><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Dade Polo, Stanley 30 oz, 1603-02..."/><button onClick={go} disabled={busy||!q.trim()}>{busy?'Searching…':'Search verified products'}</button>{error&&<div className="error">{error}</div>}<div className="matches">{rows.map((r,i)=><div className="match" key={`${r.item_number}-${i}`}><strong>{r.product_name}</strong><div>{r.item_number}</div><div className="muted">{[r.brand,r.color].filter(Boolean).join(' · ')}</div></div>)}</div></Tool>;
}

function QuoteTool(){
  const [q,setQ]=useState(''); const [qty,setQty]=useState(100); const [result,setResult]=useState(null); const [error,setError]=useState('');
  const go=async()=>{setError('');setResult(null);try{setResult(await pcna({action:'quote',q,qty:String(qty)}))}catch(e){setError(e.message)}};
  return <Tool title="Quote Request" copy="Resolve a verified product and return its decorated USD price tier for the requested quantity."><label>Product or item number</label><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Dade Polo or TM16398"/><label>Quantity</label><input type="number" min="1" value={qty} onChange={e=>setQty(e.target.value)}/><button onClick={go}>Build quote</button>{error&&<div className="error">{error}</div>}{result&&<div className="result">{`Product: ${result.product_name}\nItem Number: ${result.item_number}\nQuantity: ${result.quantity}\nMOQ Tier: ${result.moq_tier}\nUnit Price: $${Number(result.unit_price).toFixed(2)} ${result.currency}\nSchedule: ${result.schedule}\n${result.below_moq?'Note: Requested quantity is below MOQ.':''}`}</div>}</Tool>;
}

function SpecTool(){
  const [natural,setNatural]=useState(''); const [result,setResult]=useState(''); const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  const go=async()=>{
    if(!natural.trim()||busy)return;
    setBusy(true);setError('');setResult('');
    try{const d=await pcna({action:'spec_ai',q:natural.trim()});setResult(d.order||'')}
    catch(e){setError(e.message)}
    finally{setBusy(false)}
  };
  return <Tool title="Spec Sample Order" copy="Tell Nova the request in plain English. Nova interprets it, then the app resolves the verified PCNA product and decoration data before building the order."><label>Tell Nova what you need</label><textarea value={natural} onChange={e=>setNatural(e.target.value)} placeholder="Make me a spec sample order with the Dade Polo in black, medium, embroidery left chest, white imprint."/><button onClick={go} disabled={busy||!natural.trim()}>{busy?'Nova is generating…':'Generate Spec Sample Order'}</button>{busy&&<div className="success">Nova is generating your verified spec sample order…</div>}{error&&<div className="error">{error}</div>}{result&&<><div className="result">{result}</div><button className="secondary" onClick={()=>navigator.clipboard.writeText(result)}>Copy order</button></>}</Tool>;
}

function VirtualTool(){
  const [text,setText]=useState(''); const [saved,setSaved]=useState(false);
  const save=()=>{localStorage.setItem('pcna_virtual_request',text);setSaved(true)};
  return <Tool title="Virtuals / Designs" copy="Capture the complete virtual request without losing product, decoration, or art direction details."><label>Virtual request</label><textarea value={text} onChange={e=>{setText(e.target.value);setSaved(false)}} placeholder="Example: Dade Polo, black, left chest embroidery, white logo…"/><button onClick={save}>Save request</button>{saved&&<div className="success">Saved on this device.</div>}</Tool>;
}

function Projects(){
  const [name,setName]=useState(''); const [notes,setNotes]=useState(''); const [items,setItems]=useState(()=>[]); const save=()=>{const next=[...items,{name,notes}].filter(x=>x.name||x.notes);setItems(next);localStorage.setItem('pcna_projects',JSON.stringify(next));setName('');setNotes('')};
  return <Tool title="Projects" copy="Save lightweight customer/project notes on this device."><label>Project name</label><input value={name} onChange={e=>setName(e.target.value)}/><label>Notes</label><textarea value={notes} onChange={e=>setNotes(e.target.value)}/><button onClick={save}>Save project</button><div className="matches">{items.map((x,i)=><div className="match" key={i}><strong>{x.name||'Untitled Project'}</strong><div className="muted">{x.notes}</div></div>)}</div></Tool>;
}

function Tool({title,copy,children}){return <div className="tool"><a className="back" href="/?page=home">← Home</a><h1>{title}</h1><div className="copy">{copy}</div><div className="panel">{children}</div></div>}

export default function Page(){
  const sp=useSearchParams(); const page=sp.get('page')||'home';
  const content=useMemo(()=>{if(page==='search')return <SearchTool/>;if(page==='quote')return <QuoteTool/>;if(page==='spec')return <SpecTool/>;if(page==='virtual')return <VirtualTool/>;if(page==='projects')return <Projects/>;return <Home/>},[page]);
  return <main className="shell">{content}<Nav page={page}/></main>;
}
