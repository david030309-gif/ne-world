const show=async(u)=>{try{const r=await fetch(u,{signal:AbortSignal.timeout(20000),headers:{'User-Agent':'Mozilla/5.0'}});const t=await r.text();console.log('URL',u,'status',r.status,'type',r.headers.get('content-type'),'len',t.length);console.log(t.slice(0,700).replace(/\s+/g,' '));}catch(e){console.log('URL',u,'ERR',e.message)}};
for (const u of [
 'https://rss.sbb.hafas.cloud/bin/help.exe/dnl?tpl=rss_feed_custom&L=vs_rss_sbb&language=de',
 'https://rss.sbb.hafas.cloud/bin/help.exe/dnl?tpl=rss_feed_custom&icons=46&regions=BVI:1&L=vs_rss_sbb&language=de',
 'https://rss.sbb.hafas.cloud/bin/help.exe/dnl?tpl=rss_feed&L=vs_rss_sbb',
 'https://rss.sbb.hafas.cloud/bin/help.exe/dn?tpl=rss_feed_custom',
 'https://www.sbb.ch/en/plan/rail-traffic-information',
]) await show(u);
