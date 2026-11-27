const r=await fetch('https://api.tfl.gov.uk/Road/all/Disruption?stripContent=true');const a=await r.json();
const c={};for(const d of a){const k=`${d.status}|${d.severity}|${d.category}|closure=${d.hasClosures}`;c[k]=(c[k]||0)+1}
console.log('TOTAL',a.length);console.log(JSON.stringify(c));console.log(JSON.stringify(a.slice(0,2).map(d=>({...d,geography:undefined,geometry:undefined,roadDisruptionLines:undefined,roadDisruptionImpactAreas:undefined,recurringSchedules:undefined,roadProject:undefined}))).slice(0,1500));
