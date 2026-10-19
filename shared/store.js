/* Product page behaviour. Shared by every generated page; edit here, then run build.py. */

(function(){
  "use strict";
  var SITE=window.SITE||{}, BRAND=SITE.brand||"", STORE=SITE.storeUrl||"https://1examprep.com";
  var ROUTE=window.ROUTE||{};          /* set per page by a one-line inline script */
  var C=window.CATALOG||[], STATES=window.CATALOG_STATES||[];
  var TIERS=["book-fc","nec","nec-tabs","calc","super","ultimate"];
  var GENERAL="General (any state)";
  var FEATURED="ultimate";
  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){return "$"+Number(v).toFixed(2);}
  function cartUrl(variantId){return STORE+"/cart/"+variantId+":1";}
  function saving(p){var c=parseFloat(p.compareAt||0),n=parseFloat(p.price);return c>n?Math.round((c-n)/c*100):0;}
  function slugState(s){return s===GENERAL?"general":s.toLowerCase().replace(/ /g,"-");}
  function unslugState(x){x=String(x||"").toLowerCase();return STATES.concat([GENERAL]).filter(function(s){return slugState(s)===x;})[0]||null;}
  function cap(s){return s?s[0].toUpperCase()+s.slice(1).toLowerCase():s;}
  function cleanTitle(t){return t.replace(/\s*\(Based on the \d{4} NEC\)\s*/,"").replace(/: Trusted by 50k Electricians/,"");}

  /* ---- URL base: everything before this page's own route segments ---- */
  var BASE=(function(){
    if(window.__B)return window.__B;                                   /* single-page build: computed in <head> from the URL */
    var p=location.pathname.replace(/index\.html$/,"");var parts=p.split("/");if(parts[parts.length-1]==="")parts.pop();for(var i=0;i<(ROUTE.depth||0);i++)parts.pop();return parts.join("/")+"/";})();
  var hl=document.getElementById("homeLink");if(hl&&window.__B)hl.setAttribute("href",BASE);
  function pathFor(s,tier){return BASE+slugState(s.state)+"/"+s.level.toLowerCase()+"/"+s.year+"/"+(tier?tier+"/":"");}
  function parsePath(){var rel=location.pathname.slice(BASE.length).replace(/index\.html$/,"").split("/").filter(Boolean);var st=unslugState(rel[0]);if(!st)return null;var lv=cap(rel[1]||"");if(lv!=="Journeyman"&&lv!=="Master")return null;return {state:st,level:lv,year:(rel[2]&&/^\d{4}$/.test(rel[2]))?rel[2]:null,tier:rel[3]||null};}

  var years=C.map(function(p){return p.year;}).filter(function(y,i,a){return y&&a.indexOf(y)===i;}).sort().reverse();
  function yearsFor(state,level){var st=state===GENERAL?null:state;return years.filter(function(y){return C.some(function(p){return p.state===st&&p.level===level&&p.year===y;});});}

  /* ---- selection ---- */
  var sel={state:"Texas",level:"Journeyman",year:years[0]};
  try{var saved=JSON.parse(localStorage.getItem("oep-sel")||"null");if(saved&&saved.state&&saved.level)sel={state:saved.state,level:saved.level,year:saved.year||years[0]};}catch(e){}
  var fromUrl=parsePath();
  if(ROUTE.state){sel.state=ROUTE.state==="general"?GENERAL:(unslugState(ROUTE.state)||sel.state);sel.level=ROUTE.level||sel.level;sel.year=ROUTE.year||sel.year;}
  else if(fromUrl){sel.state=fromUrl.state;sel.level=fromUrl.level;if(fromUrl.year)sel.year=fromUrl.year;}
  var openTier=ROUTE.tier||(fromUrl&&fromUrl.tier)||null;
  var onRoutePage=!!(ROUTE.state||fromUrl);   /* root page keeps its URL until the visitor changes something */

  /* custom searchable state picker (same look everywhere, no native dropdown) */
  function makePicker(host){
    var all=STATES.concat([GENERAL]), open=false;
    host.innerHTML='<button type="button" class="spick-btn" aria-haspopup="listbox" aria-expanded="false"><span class="spick-val"></span><i></i></button>'+
      '<div class="spick-pop" hidden><input type="search" class="spick-q" placeholder="Type a state\u2026" autocomplete="off" aria-label="Search states"><div class="spick-list" role="listbox"></div></div>';
    var btn=host.querySelector(".spick-btn"), val=host.querySelector(".spick-val"), pop=host.querySelector(".spick-pop"), q=host.querySelector(".spick-q"), list=host.querySelector(".spick-list");
    function draw(filter){var f=(filter||"").toLowerCase();list.innerHTML=all.filter(function(st){return !f||st.toLowerCase().indexOf(f)>-1||slugState(st).indexOf(f)>-1;}).map(function(st){return '<button type="button" role="option" data-v="'+esc(st)+'" aria-selected="'+(st===sel.state)+'"'+(st===GENERAL?' class="gen"':'')+'>'+esc(st)+'</button>';}).join("")||'<p class="spick-none">No match</p>';}
    function show(){open=true;pop.hidden=false;document.documentElement.classList.add("spick-open");btn.setAttribute("aria-expanded","true");q.value="";draw();setTimeout(function(){q.focus();},10);var cur=list.querySelector('[aria-selected="true"]');if(cur)cur.scrollIntoView({block:"center"});}
    function hide(){open=false;pop.hidden=true;document.documentElement.classList.remove("spick-open");btn.setAttribute("aria-expanded","false");}
    btn.addEventListener("click",function(){open?hide():show();});
    q.addEventListener("input",function(){draw(q.value);});
    q.addEventListener("keydown",function(e){if(e.key==="Enter"){var f=list.querySelector("[data-v]");if(f){f.click();}}if(e.key==="ArrowDown"){var f2=list.querySelector("[data-v]");if(f2)f2.focus();e.preventDefault();}});
    list.addEventListener("keydown",function(e){var b=e.target.closest("[data-v]");if(!b)return;if(e.key==="ArrowDown"&&b.nextElementSibling){b.nextElementSibling.focus();e.preventDefault();}if(e.key==="ArrowUp"){(b.previousElementSibling||q).focus();e.preventDefault();}});
    list.addEventListener("click",function(e){var b=e.target.closest("[data-v]");if(!b)return;hide();if(b.getAttribute("data-v")!==sel.state){sel.state=b.getAttribute("data-v");navigate();}btn.focus();});
    document.addEventListener("click",function(e){if(open&&!host.contains(e.target))hide();});
    document.addEventListener("keydown",function(e){if(e.key==="Escape"&&open){hide();btn.focus();}});
    return {set:function(v){val.textContent=v;}};
  }
  var selects=Array.prototype.map.call(document.querySelectorAll("[data-state-pick]"),makePicker);
  selects.forEach(function(s){s.set(sel.state);});
  document.querySelectorAll("[data-level]").forEach(function(b){b.addEventListener("click",function(){sel.level=b.getAttribute("data-level");navigate();});});
  var yearSels=document.querySelectorAll("[data-year-sel]");
  yearSels.forEach(function(s){s.addEventListener("change",function(){sel.year=s.value;navigate();});});

  function productsFor(state,level,year){
    var seen={}, st=state===GENERAL?null:state;
    return C.filter(function(p){return p.state===st&&p.level===level&&p.year===year&&TIERS.indexOf(p.tier)>-1;})
      .sort(function(a,b){return a.rank-b.rank||a.id.localeCompare(b.id);})
      .filter(function(p){if(seen[p.tier])return false;seen[p.tier]=1;return true;});
  }
  function cardHTML(p){
    var sv=saving(p), feat=p.tier===FEATURED;
    return '<article class="pc'+(feat?" pc--featured":"")+'" data-id="'+esc(p.id)+'">'+
      (feat?'<span class="pc-badge">Most complete</span>':'')+
      '<div class="pc-img"><img src="'+esc(p.image)+'" alt="'+esc(cleanTitle(p.title))+'" loading="lazy"></div>'+
      '<div class="pc-body">'+
        '<span class="pc-tier">'+esc((p.state||"Any state")+" · "+p.level+" · "+p.year)+'</span>'+
        '<h3 class="pc-name">'+esc(p.tierName)+'</h3>'+
        '<p class="pc-sub">'+esc(cleanTitle(p.title))+'</p>'+
        '<p class="pc-desc">'+esc(p.desc.replace(p.title,"").trim())+'</p>'+
        '<div class="pc-price"><span class="pc-now">'+money(p.price)+'</span>'+(p.compareAt&&parseFloat(p.compareAt)>parseFloat(p.price)?'<s class="pc-was">'+money(p.compareAt)+'</s><span class="pc-save">Save '+sv+'%</span>':'')+'</div>'+
        '<div class="pc-actions"><a class="btn btn-buy" href="'+esc(cartUrl(p.variants[0].id))+'" rel="noopener">Buy now</a><a class="btn btn-details" href="'+esc(pathFor(sel,p.tierSlug))+'" data-details="'+esc(p.id)+'" data-tier="'+esc(p.tierSlug)+'">What’s inside</a></div>'+
      '</div></article>';
  }
  function h1Words(text){var i=0;return text.split(/\s+/).map(function(w){return '<span class="w'+(/^\*/.test(w)?" hl":"")+'" style="--n:'+(i++)+'">'+esc(w.replace(/^\*/,""))+'</span>';}).join(" ");}
  function pageTitle(){return (sel.state===GENERAL?"":sel.state+" ")+sel.level+" Electrician Exam Prep ("+sel.year+" NEC) | "+BRAND;}
  function render(){
    try{localStorage.setItem("oep-sel",JSON.stringify(sel));}catch(e){}
    var ys=yearsFor(sel.state,sel.level); if(ys.length&&ys.indexOf(sel.year)<0)sel.year=ys[0];
    selects.forEach(function(s){s.set(sel.state);});
    document.querySelectorAll("[data-level]").forEach(function(b){b.setAttribute("aria-pressed",String(b.getAttribute("data-level")===sel.level));});
    yearSels.forEach(function(s){s.innerHTML=ys.map(function(y){return '<option value="'+y+'">'+y+' NEC</option>';}).join("");s.value=sel.year;});
    document.querySelectorAll(".yearfield").forEach(function(el){el.hidden=years.length<2;});
    document.getElementById("selTitle").textContent=sel.state+" · "+sel.level+" · "+sel.year;
    document.getElementById("crumb").innerHTML='<a href="'+esc(BASE)+'">All states</a><span>/</span><a href="'+esc(pathFor(sel))+'">'+esc(sel.state)+'</a><span>/</span><a href="'+esc(pathFor(sel))+'">'+esc(sel.level)+'</a><span>/</span><a href="'+esc(pathFor(sel))+'">'+esc(sel.year)+'</a>';
    var list=productsFor(sel.state,sel.level,sel.year), rail=document.getElementById("rail");
    rail.innerHTML=list.length?list.map(cardHTML).join(""):'<div class="empty">No '+esc(sel.level.toLowerCase())+' packages found for '+esc(sel.state)+' ('+esc(sel.year)+'). Try the other level or the study guides below.</div>';
    var feat=list.filter(function(p){return p.tier===FEATURED;})[0]||list[0];
    if(feat){document.getElementById("stickyTitle").textContent=sel.state+" "+sel.level+" · "+feat.tierName;document.getElementById("stickyPrice").textContent=money(feat.price)+" · straight to checkout";document.getElementById("stickyBuy").href=cartUrl(feat.variants[0].id);}
    if(onRoutePage){
      document.title=pageTitle();
      document.getElementById("h1").innerHTML=h1Words((sel.state===GENERAL?"Any state.":sel.state+".")+" *"+sel.level+". "+sel.year+" code.");
      document.getElementById("lead").textContent=sel.level+" electrician exam prep for "+(sel.state===GENERAL?"any state":sel.state)+", built on the "+sel.year+" National Electrical Code. Choose how much help you want, from the study guide alone to the Ultimate Combo.";
    }
    return list;
  }
  function navigate(){
    onRoutePage=true; render();
    var p=pathFor(sel); if(location.pathname!==p&&history.pushState)history.pushState({sel:sel},"",p);
    closeModal(false);
  }
  document.getElementById("goBtn").addEventListener("click",function(e){e.preventDefault();navigate();document.getElementById("packs").scrollIntoView({behavior:"smooth"});});
  window.addEventListener("popstate",function(){var r=parsePath();if(!r)return;sel.state=r.state;sel.level=r.level;if(r.year)sel.year=r.year;onRoutePage=true;render();closeModal(false);});

  /* mobile rail arrows + position */
  (function(){var rail=document.getElementById("rail"),pos=document.getElementById("railpos"),nav=document.getElementById("railnav");
    function cards(){return Array.prototype.slice.call(rail.querySelectorAll(".pc"));}
    function idx(){var cs=cards(),r=rail.getBoundingClientRect(),best=0,bd=1e9;cs.forEach(function(c,i){var d=Math.abs(c.getBoundingClientRect().left+c.offsetWidth/2-(r.left+r.width/2));if(d<bd){bd=d;best=i;}});return best;}
    function upd(){var cs=cards();pos.textContent=(cs.length?idx()+1:0)+" / "+cs.length;nav.hidden=cs.length<2;}
    rail.addEventListener("scroll",function(){requestAnimationFrame(upd);},{passive:true});
    nav.addEventListener("click",function(e){var b=e.target.closest("[data-dir]");if(!b)return;var cs=cards(),i=Math.max(0,Math.min(cs.length-1,idx()+(+b.getAttribute("data-dir"))));cs[i].scrollIntoView({behavior:"smooth",block:"nearest",inline:"center"});});
    new MutationObserver(upd).observe(rail,{childList:true});upd();})();

  /* singles (no state) */
  var singles=C.filter(function(p){return !p.state&&p.rank===0;}).sort(function(a,b){return parseFloat(a.price)-parseFloat(b.price);});
  document.getElementById("singlesGrid").innerHTML=singles.map(function(p){
    return '<article class="sg" data-id="'+esc(p.id)+'"><div class="pc-img"><img src="'+esc(p.image)+'" alt="'+esc(cleanTitle(p.title))+'" loading="lazy"></div><div class="pc-body">'+
      '<span class="pc-tier">'+esc(p.level==="General"?"All levels":p.level)+'</span><h3 class="pc-name">'+esc(cleanTitle(p.title))+'</h3>'+
      '<div class="pc-price"><span class="pc-now">'+money(p.price)+'</span>'+(p.maxPrice!==p.price?'<small style="color:var(--muted)"> to '+money(p.maxPrice)+'</small>':'')+'</div>'+
      '<div class="pc-actions"><a class="btn btn-buy" href="'+esc(cartUrl(p.variants[0].id))+'" rel="noopener">Buy now</a><button class="btn btn-details" type="button" data-details="'+esc(p.id)+'">What’s inside</button></div></div></article>';
  }).join("");

  /* marquee of states */
  var mq=STATES.map(function(s){return '<span><a href="'+esc(BASE+slugState(s)+"/journeyman/"+years[0]+"/")+'" style="color:inherit;text-decoration:none">'+esc(s)+'</a></span>';}).join("");
  document.getElementById("marq").innerHTML=mq+mq;

  /* modal */
  var modal=document.getElementById("product-modal"), lastFocus=null, baseTitle=document.title;
  function openModal(id,push){
    var p=C.filter(function(x){return x.id===id;})[0]; if(!p) return;
    var opts=p.variants.map(function(v,i){return '<label class="m-opt"><input type="radio" name="v" value="'+esc(v.id)+'"'+(i===0?" checked":"")+'><span>'+esc(v.title)+'</span><b>'+money(v.price)+(v.compareAt&&parseFloat(v.compareAt)>parseFloat(v.price)?'<s>'+money(v.compareAt)+'</s>':'')+'</b></label>';}).join("");
    modal.querySelector(".modal-body").innerHTML=
      '<div class="m-img"><img src="'+esc(p.image)+'" alt=""></div>'+
      '<div class="m-txt"><span class="m-tier">'+esc((p.state?p.state+" · ":"")+p.level+" · "+p.tierName)+'</span>'+
      '<h2 id="modal-title" class="modal-title">'+esc(p.title)+'</h2>'+
      '<p class="modal-desc">'+esc(p.desc.replace(p.title,"").trim())+'</p>'+
      '<div class="m-foot"><div class="m-opts">'+opts+'</div>'+
      '<a class="btn btn-buy btn-buy--lg" id="m-buy" href="'+esc(cartUrl(p.variants[0].id))+'" rel="noopener">Buy now — go to checkout</a></div></div>';
    modal.querySelectorAll('input[name="v"]').forEach(function(r){r.addEventListener("change",function(){document.getElementById("m-buy").href=cartUrl(r.value);});});
    lastFocus=document.activeElement; modal.classList.add("is-open"); modal.setAttribute("aria-hidden","false"); document.documentElement.classList.add("modal-open");
    document.getElementById("m-buy").focus();
    if(p.state!==undefined&&p.rank>0){ baseTitle=document.title; document.title=cleanTitle(p.title)+" | "+BRAND;
      if(push!==false&&history.pushState){var tp=pathFor(sel,p.tierSlug);if(location.pathname!==tp)history.pushState({sel:sel,tier:p.tierSlug},"",tp);} }
  }
  function closeModal(pop){
    if(!modal.classList.contains("is-open"))return;
    modal.classList.remove("is-open");modal.setAttribute("aria-hidden","true");document.documentElement.classList.remove("modal-open");if(lastFocus&&lastFocus.focus)lastFocus.focus();
    if(onRoutePage){document.title=pageTitle();}
    if(pop!==false&&onRoutePage&&history.replaceState){var lp=pathFor(sel);if(location.pathname!==lp)history.replaceState({sel:sel},"",lp);}
  }
  document.addEventListener("click",function(e){var t=e.target.closest("[data-details],[data-close]");if(!t)return;
    if(t.hasAttribute("data-details")){var p=C.filter(function(x){return x.id===t.getAttribute("data-details");})[0];
      if(p&&p.rank>0&&t.tagName==="A")return;            /* state packages have their own page: follow the link */
      e.preventDefault();openModal(t.getAttribute("data-details"),false);}
    else{e.preventDefault();closeModal(true);}});
  document.addEventListener("keydown",function(e){if(e.key==="Escape")closeModal(true);});

  /* reveal + count */
  var io=("IntersectionObserver" in window)?new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add("in");io.unobserve(en.target);}});},{threshold:.15}):null;
  document.querySelectorAll("[data-reveal]").forEach(function(el){io?io.observe(el):el.classList.add("in");});
  var reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-count]").forEach(function(el){var end=+el.getAttribute("data-count");if(reduce){el.textContent=end;return;}var t0=null;(function step(ts){if(!t0)t0=ts;var k=Math.min(1,(ts-t0)/1400);el.textContent=Math.round(end*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(step);})(performance.now());});
  document.querySelectorAll("[data-year]").forEach(function(el){el.textContent=new Date().getFullYear();});
  document.documentElement.classList.add("js");
  render();
})();
