/* Admin dashboard: Google Analytics 4 (Data API, read-only, signed in as you), catalog table, GitHub sync status. */
(function(){
  "use strict";
  var A=window.ADMIN||{}, C=window.CATALOG||[], GENERAL="General (any state)";
  var $=function(id){return document.getElementById(id);};
  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function n(v){return Number(v||0).toLocaleString("en-US");}
  function money(v){return "$"+Number(v||0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});}
  function slugState(s){return s===GENERAL?"general":s.toLowerCase().replace(/ /g,"-");}
  function pill(id,cls,text){var p=$(id);p.className="pill "+cls;p.innerHTML="<i></i>"+esc(text);}

  /* ---------- catalog ---------- */
  (function(){
    var m=(document.scripts[1]&&document.scripts[1].src)?null:null;
    var pulled=(function(){var s=document.querySelector('script[src$="catalog.js"]');return null;})();
    $("cCount").textContent=n(C.length);
    var combos={}, dup=0, pages=0, lo=1e9, hi=0, seen={};
    var dupList=[];
    C.forEach(function(p){var k=(p.state||"General")+"|"+p.level+"|"+p.year;if(p.rank>0){combos[k]=1;var kk=k+"|"+p.tier;if(seen[kk]){dup++;dupList.push((p.state||"General")+" "+p.level+" "+p.tierName);}else{seen[kk]=1;pages++;}}lo=Math.min(lo,+p.price);hi=Math.max(hi,+p.price);});
    $("cCombos").textContent=n(Object.keys(combos).length); $("cPages").textContent=n(pages); $("cPrice").textContent=money(lo)+" – "+money(hi); $("cDupes").textContent=n(dup);
    if(dupList.length){var sub=$("cDupes").nextElementSibling;sub.textContent=dupList.join("; ");sub.title="These products exist twice in Shopify with the same title (handle ends in -1). The site shows one.";}
    fetch("../shared/catalog.js",{cache:"no-store"}).then(function(r){return r.text();}).then(function(t){var mm=t.match(/pulled (\d{4}-\d{2}-\d{2})/);if(mm)$("cPulled").textContent="pulled from Shopify "+mm[1];}).catch(function(){});
    var rows=C.slice().sort(function(a,b){return (a.state||"zz").localeCompare(b.state||"zz")||a.level.localeCompare(b.level)||a.rank-b.rank;});
    function draw(f){
      f=(f||"").toLowerCase();
      $("cTable").querySelector("tbody").innerHTML=rows.filter(function(p){return !f||((p.state||"general")+" "+p.level+" "+p.tierName+" "+p.price+" "+p.title).toLowerCase().indexOf(f)>-1;}).slice(0,600).map(function(p){
        var page=p.rank>0?("../"+slugState(p.state||GENERAL)+"/"+p.level.toLowerCase()+"/"+p.year+"/"+p.tierSlug+"/"):"../#singles";
        return "<tr><td>"+esc(p.state||"General")+"</td><td>"+esc(p.level)+"</td><td>"+esc(p.tierName)+"</td><td class=num>"+money(p.price)+"</td><td class=num>"+(p.compareAt?money(p.compareAt):"")+"</td><td>"+p.variants.length+"</td><td><a class=lnk href=\""+esc(page)+"\">open</a></td><td><a class=lnk href=\""+esc(p.url)+"\" target=_blank rel=noopener>store</a></td></tr>";}).join("");
    }
    draw(""); $("cQ").addEventListener("input",function(){draw($("cQ").value);});
  })();

  /* ---------- system: GitHub ---------- */
  (function(){
    var repo=A.repo; if(!repo){ $("runs").innerHTML='<div class="empty">Set "repo" in site-config.json</div>'; $("commits").innerHTML=""; return; }
    fetch("https://api.github.com/repos/"+repo+"/actions/workflows/sync-shopify.yml/runs?per_page=6").then(function(r){return r.json();}).then(function(d){
      var runs=(d.workflow_runs||[]);
      if(!runs.length){$("runs").innerHTML='<div class="empty">No runs yet. Add the two Shopify secrets in the repo settings, then run it from the Actions tab.</div>';pill("pSync","","Sync: not run yet");return;}
      $("runs").innerHTML=runs.map(function(r){var ok=r.conclusion==="success";return '<div class="bar"><div class="lab"><i class="'+(ok?"":"s2")+'" style="width:10px"></i><span>'+esc(new Date(r.created_at).toLocaleString())+' · '+esc(r.event)+' · <a class="lnk" href="'+esc(r.html_url)+'" target="_blank" rel="noopener">'+esc(r.conclusion||r.status)+'</a></span></div><b></b></div>';}).join("");
      var last=runs[0]; pill("pSync",last.conclusion==="success"?"ok":(last.status!=="completed"?"run":"bad"),"Sync: "+(last.conclusion||last.status)+" "+new Date(last.created_at).toLocaleDateString());
    }).catch(function(){$("runs").innerHTML='<div class="empty">Could not reach GitHub.</div>';});
    fetch("https://api.github.com/repos/"+repo+"/commits?per_page=6").then(function(r){return r.json();}).then(function(d){
      $("commits").innerHTML=(d||[]).map(function(c){return '<div class="bar"><div class="lab"><i style="width:10px"></i><span>'+esc(new Date(c.commit.author.date).toLocaleString())+' · <a class="lnk" href="'+esc(c.html_url)+'" target="_blank" rel="noopener">'+esc(c.commit.message.split("\n")[0])+'</a></span></div><b></b></div>';}).join("");
      if(d&&d[0]) pill("pSite","ok","Site updated "+new Date(d[0].commit.author.date).toLocaleDateString());
    }).catch(function(){});
    $("links").innerHTML=['<a class="lnk" href="../" target="_blank">Live site</a>','<a class="lnk" href="../sitemap.xml" target="_blank">sitemap.xml</a>','<a class="lnk" href="../robots.txt" target="_blank">robots.txt</a>','<a class="lnk" href="../llms.txt" target="_blank">llms.txt</a>',
      '<a class="lnk" href="https://github.com/'+esc(repo)+'" target="_blank" rel="noopener">GitHub repo</a>','<a class="lnk" href="https://github.com/'+esc(repo)+'/actions" target="_blank" rel="noopener">Actions (sync runs)</a>',
      A.ga4PropertyId?'<a class="lnk" href="https://analytics.google.com/analytics/web/#/p'+esc(A.ga4PropertyId)+'/reports/intelligenthome" target="_blank" rel="noopener">Open Google Analytics</a>':'','<a class="lnk" href="https://search.google.com/search-console" target="_blank" rel="noopener">Search Console</a>'].filter(Boolean).join(" · ");
  })();

  /* ---------- analytics (GA4 Data API) ---------- */
  var token=null, days=28;
  function setup(){
    var missing=[]; if(!A.gtagId)missing.push("<code>gtagId</code> (GA4 measurement ID, G-…)"); if(!A.ga4PropertyId)missing.push("<code>ga4PropertyId</code> (numeric property ID from GA4 Admin → Property details)"); if(!A.googleOAuthClientId)missing.push("<code>googleOAuthClientId</code> (OAuth client ID from Google Cloud Console → APIs & Services → Credentials → OAuth client, type Web, authorized JavaScript origin = this site's address)");
    if(missing.length){ $("setupNote").hidden=false; $("setupNote").innerHTML="<b>Analytics is not connected yet.</b> Add these to <code>site-config.json</code> and rebuild:<ol>"+missing.map(function(x){return "<li>"+x+"</li>";}).join("")+"</ol>Catalog and sync status below work without it."; pill("pGa","","Analytics: not set up"); return false; }
    pill("pGa","","Analytics: sign in"); $("signin").hidden=false; return true;
  }
  function signIn(){
    if(!window.google||!google.accounts){alert("Google sign-in script has not loaded yet. Try again in a moment.");return;}
    var tc=google.accounts.oauth2.initTokenClient({client_id:A.googleOAuthClientId,scope:"https://www.googleapis.com/auth/analytics.readonly",callback:function(r){if(r&&r.access_token){token=r.access_token;$("signin").textContent="Refresh";pill("pGa","ok","Analytics: connected");load();}}});
    tc.requestAccessToken();
  }
  function report(body){
    return fetch("https://analyticsdata.googleapis.com/v1beta/properties/"+A.ga4PropertyId+":runReport",{method:"POST",headers:{Authorization:"Bearer "+token,"Content-Type":"application/json"},body:JSON.stringify(Object.assign({dateRanges:[{startDate:days+"daysAgo",endDate:"today"}]},body))})
      .then(function(r){return r.json();}).then(function(d){if(d.error)throw d.error;return d;});
  }
  function rowsOf(d,dimIdx,metIdx){return (d.rows||[]).map(function(r){return {k:r.dimensionValues[dimIdx||0].value,v:Number(r.metricValues[metIdx||0].value)};});}
  function bars(id,rows,fmt,cls){
    var el=$(id); if(!rows.length){el.innerHTML='<div class="empty">No data in this range.</div>';return;}
    var max=Math.max.apply(null,rows.map(function(r){return r.v;}))||1;
    el.innerHTML=rows.map(function(r){return '<div class="bar"><div class="lab"><i class="'+(cls||"")+'" style="width:'+Math.max(4,Math.round(r.v/max*100))+'%"></i><span title="'+esc(r.k)+'">'+esc(r.k)+'</span></div><b>'+(fmt||n)(r.v)+'</b></div>';}).join("");
  }
  function line(id,series,cls){
    var host=$(id); if(!series.length){host.innerHTML='<div class="empty">No data in this range.</div>';return;}
    var W=600,H=220,pl=36,pr=8,pt=12,pb=26, max=Math.max.apply(null,series.map(function(s){return s.v;}))||1;
    var x=function(i){return pl+(series.length===1?0:i*(W-pl-pr)/(series.length-1));}, y=function(v){return pt+(H-pt-pb)*(1-v/max);};
    var pts=series.map(function(s,i){return [x(i),y(s.v)];});
    var path="M"+pts.map(function(p){return p[0].toFixed(1)+" "+p[1].toFixed(1);}).join("L");
    var area=path+"L"+pts[pts.length-1][0].toFixed(1)+" "+(H-pb)+"L"+pts[0][0].toFixed(1)+" "+(H-pb)+"Z";
    var ticks=[0,.5,1].map(function(f){return '<line class="ax" x1="'+pl+'" x2="'+(W-pr)+'" y1="'+y(max*f)+'" y2="'+y(max*f)+'"/><text class="lbl" x="'+(pl-6)+'" y="'+(y(max*f)+4)+'" text-anchor="end">'+n(Math.round(max*f))+'</text>';}).join("");
    var step=Math.max(1,Math.round(series.length/6));
    var xl=series.map(function(s,i){return i%step===0?'<text class="lbl" x="'+x(i)+'" y="'+(H-6)+'" text-anchor="middle">'+esc(s.k.slice(5))+'</text>':"";}).join("");
    host.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(id)+'">'+ticks+'<path class="ar '+(cls||"")+'" d="'+area+'"/><path class="ln '+(cls||"")+'" d="'+path+'"/><line class="xh" id="'+id+'xh" y1="'+pt+'" y2="'+(H-pb)+'"/>'+
      pts.map(function(p,i){return '<circle class="dot '+(cls||"")+'" data-i="'+i+'" cx="'+p[0]+'" cy="'+p[1]+'" r="4"/>';}).join("")+xl+'<rect class="hit" x="'+pl+'" y="0" width="'+(W-pl-pr)+'" height="'+H+'"/></svg><div class="tip" id="'+id+'tip"></div>';
    var svg=host.querySelector("svg"), tip=$(id+"tip"), xh=$(id+"xh"), dots=host.querySelectorAll(".dot");
    svg.addEventListener("mousemove",function(e){var r=svg.getBoundingClientRect();var mx=(e.clientX-r.left)/r.width*W;var i=0,bd=1e9;pts.forEach(function(p,k){var d=Math.abs(p[0]-mx);if(d<bd){bd=d;i=k;}});
      dots.forEach(function(d,k){d.classList.toggle("on",k===i);});xh.setAttribute("x1",pts[i][0]);xh.setAttribute("x2",pts[i][0]);xh.classList.add("on");
      tip.textContent=series[i].k+": "+n(series[i].v);tip.style.left=(pts[i][0]/W*r.width)+"px";tip.style.top=(pts[i][1]/H*r.height)+"px";tip.classList.add("on");});
    svg.addEventListener("mouseleave",function(){dots.forEach(function(d){d.classList.remove("on");});xh.classList.remove("on");tip.classList.remove("on");});
  }
  function load(){
    if(!token) return;
    var ids=["cSessions","cBuy"]; ids.forEach(function(i){$(i).innerHTML='<div class="empty">Loading…</div>';});
    Promise.all([
      report({dimensions:[{name:"date"}],metrics:[{name:"sessions"},{name:"totalUsers"},{name:"screenPageViews"}],orderBys:[{dimension:{dimensionName:"date"}}]}),
      report({dimensions:[{name:"eventName"}],metrics:[{name:"eventCount"}],orderBys:[{metric:{metricName:"eventCount"},desc:true}],limit:40}),
      report({dimensions:[{name:"date"}],metrics:[{name:"eventCount"}],dimensionFilter:{filter:{fieldName:"eventName",stringFilter:{value:"buy_now_click"}}},orderBys:[{dimension:{dimensionName:"date"}}]}),
      report({dimensions:[{name:"itemCategory2"}],metrics:[{name:"itemsCheckedOut"}],orderBys:[{metric:{metricName:"itemsCheckedOut"},desc:true}],limit:12}),
      report({dimensions:[{name:"itemCategory3"}],metrics:[{name:"itemsCheckedOut"}],orderBys:[{metric:{metricName:"itemsCheckedOut"},desc:true}],limit:10}),
      report({dimensions:[{name:"itemCategory"}],metrics:[{name:"itemsCheckedOut"}],orderBys:[{metric:{metricName:"itemsCheckedOut"},desc:true}],limit:5}),
      report({dimensions:[{name:"pagePath"}],metrics:[{name:"screenPageViews"}],orderBys:[{metric:{metricName:"screenPageViews"},desc:true}],limit:12}),
      report({dimensions:[{name:"sessionSourceMedium"}],metrics:[{name:"sessions"}],orderBys:[{metric:{metricName:"sessions"},desc:true}],limit:10}),
      report({dimensions:[{name:"deviceCategory"}],metrics:[{name:"sessions"}],orderBys:[{metric:{metricName:"sessions"},desc:true}]}),
      report({dimensions:[{name:"searchTerm"}],metrics:[{name:"eventCount"}],dimensionFilter:{filter:{fieldName:"eventName",stringFilter:{value:"search"}}},orderBys:[{metric:{metricName:"eventCount"},desc:true}],limit:12}).catch(function(){return {rows:[]};}),
      report({metrics:[{name:"eventValue"}],dimensionFilter:{filter:{fieldName:"eventName",stringFilter:{value:"begin_checkout"}}}}).catch(function(){return {rows:[]};}),
      report({dimensions:[{name:"customEvent:button_location"}],metrics:[{name:"eventCount"}],dimensionFilter:{filter:{fieldName:"eventName",stringFilter:{value:"buy_now_click"}}},orderBys:[{metric:{metricName:"eventCount"},desc:true}]}).catch(function(){return null;})
    ]).then(function(R){
      var daily=R[0].rows||[], tot=function(i){return daily.reduce(function(a,r){return a+Number(r.metricValues[i].value);},0);};
      $("kSessions").textContent=n(tot(0)); $("kUsers").textContent=n(tot(1))+" users"; $("kViews").textContent=n(tot(2));
      var ev={}; rowsOf(R[1]).forEach(function(r){ev[r.k]=r.v;});
      var buy=ev.buy_now_click||0; $("kBuy").textContent=n(buy); $("kBuyRate").textContent=tot(0)?((buy/tot(0)*100).toFixed(1)+"% of sessions"):"";
      $("kPhone").textContent=n(ev.phone_click||0); $("kSearch").textContent=n(ev.search||0);
      var val=R[10].rows&&R[10].rows[0]?Number(R[10].rows[0].metricValues[0].value):0; $("kValue").textContent=money(val);
      line("cSessions",daily.map(function(r){return {k:r.dimensionValues[0].value.replace(/(\d{4})(\d{2})(\d{2})/,"$1-$2-$3"),v:Number(r.metricValues[0].value)};}));
      var bd={}; rowsOf(R[2]).forEach(function(r){bd[r.k]=r.v;});
      line("cBuy",daily.map(function(r){var k=r.dimensionValues[0].value;return {k:k.replace(/(\d{4})(\d{2})(\d{2})/,"$1-$2-$3"),v:bd[k]||0};}),"s2");
      bars("bState",rowsOf(R[3]).filter(function(r){return r.k!=="(not set)";}),null,"s2"); bars("bTier",rowsOf(R[4]).filter(function(r){return r.k!=="(not set)";}),null,"s2"); bars("bLevel",rowsOf(R[5]).filter(function(r){return r.k!=="(not set)";}),null,"s2");
      bars("bEvents",rowsOf(R[1])); bars("bPages",rowsOf(R[6])); bars("bSource",rowsOf(R[7])); bars("bDevice",rowsOf(R[8])); bars("bSearch",rowsOf(R[9]));
      if(R[11]) bars("bLoc",rowsOf(R[11]).filter(function(r){return r.k!=="(not set)";}),null,"s2"); else $("bLoc").innerHTML='<div class="empty">In GA4: Admin → Custom definitions → Create custom dimension, event scope, parameter <code>button_location</code>. Data appears from then on.</div>';
    }).catch(function(e){ids.forEach(function(i){$(i).innerHTML='<div class="empty">'+esc((e&&e.message)||"Could not load analytics")+'</div>';});pill("pGa","bad","Analytics: error");});
  }
  if(setup()){ $("signin").addEventListener("click",signIn); }
  $("range").addEventListener("click",function(e){var b=e.target.closest("[data-days]");if(!b)return;days=+b.getAttribute("data-days");$("range").querySelectorAll("button").forEach(function(x){x.setAttribute("aria-pressed",String(x===b));});load();});
})();
