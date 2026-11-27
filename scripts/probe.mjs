const show=async(u)=>{try{const r=await fetch(u,{signal:AbortSignal.timeout(20000)});const t=await r.text();console.log('URL',u,'status',r.status,'len',t.length);console.log(t.slice(0,1500));}catch(e){console.log('URL',u,'ERR',e.message)}};
await show('https://data.sbb.ch/api/explore/v2.1/catalog/datasets/rail-traffic-information/records?limit=3&order_by=startdatetime%20desc&select=title,published,startdatetime,enddatetime,type');
await show('https://data.sbb.ch/api/explore/v2.1/catalog/datasets/rail-traffic-information?select=metas');
await show('https://data.sbb.ch/api/explore/v2.1/catalog/datasets/rail-traffic-information/records?limit=5&where=enddatetime%3E%3Dnow()&select=title,published,startdatetime,enddatetime,type');
