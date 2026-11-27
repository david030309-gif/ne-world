const show=async(u,o={})=>{try{const r=await fetch(u,{...o,signal:AbortSignal.timeout(20000)});const t=await r.text();console.log('URL',u,'status',r.status,'len',t.length);console.log(t.slice(0,2500));}catch(e){console.log('URL',u,'ERR',e.message)}};
await show('https://data.sbb.ch/api/explore/v2.1/catalog/datasets/rail-traffic-information/records?limit=2&order_by=published%20desc');
await show('https://www.alert.swiss/content/alertswiss-internet/en/home/_jcr_content/polyalert.alertswiss_alerts.actual.json');
