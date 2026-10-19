/* Site search over shared/site-index.js (written by build.py): licenses first, then products.
   Opens from the header button or the "/" key; /search/?q= renders the same results on a page. */
(function(){
  "use strict";
  var ROUTE=window.ROUTE||{};
  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){v=Number(v);return "$"+(v%1?v.toFixed(2):String(v)).replace(/\B(?=(\d{3})+(?!\d))/g,",");}
  var BASE=(function(){var p=location.pathname.replace(/index\.html$/,"");var parts=p.split("/");if(parts[parts.length-1]==="")parts.pop();for(var i=0;i<(ROUTE.depth||0);i++)parts.pop();return parts.join("/")+"/";})();

  var ov=document.createElement("div"); ov.id="search"; ov.className="srch"; ov.hidden=true; ov.setAttribute("aria-hidden","true");
  ov.innerHTML='<div class="srch-back" data-sclose></div><div class="srch-box" role="dialog" aria-modal="true" aria-label="Search">'+
    '<form class="srch-form" role="search" action="'+esc(BASE)+'search/" method="get"><input class="srch-q" name="q" type="search" placeholder="Search a license, package or product" autocomplete="off" aria-label="Search"><button type="button" class="srch-x" data-sclose aria-label="Close">×</button></form>'+
    '<div class="srch-res" id="srchRes" aria-live="polite"></div><p class="srch-hint">Try “roofing”, “master plumber”, “tabbed” or “building inspector”. Press Esc to close.</p></div>';
  document.body.appendChild(ov);
  var q=ov.querySelector(".srch-q"), res=document.getElementById("srchRes"), opener=null;

  function ensureIndex(cb){
    if(window.SITE_INDEX){cb();return;}
    if(ensureIndex.loading){ensureIndex.cbs.push(cb);return;}
    ensureIndex.loading=true; ensureIndex.cbs=[cb];
    var s=document.createElement("script"); s.src=BASE+"shared/site-index.js"; s.onload=function(){ensureIndex.cbs.forEach(function(f){f();});}; document.head.appendChild(s);
  }
  function tokens(s){return s.toLowerCase().replace(/[^a-z0-9+ ]/g," ").split(/\s+/).filter(function(w){return w&&["virginia","va","exam","prep","the","and","for"].indexOf(w)<0;});}
  function search(text){
    var I=window.SITE_INDEX||{classes:[],products:[]}, t=tokens(text); if(!t.length) return {classes:[],products:[]};
    function score(hay,boost){hay=hay.toLowerCase();var sc=0;t.forEach(function(w){if(hay.indexOf(w)>-1)sc+=1+(boost&&boost.toLowerCase().indexOf(w)>-1?1:0);});return t.every(function(w){return hay.indexOf(w)>-1;})?sc+5:sc;}
    var cl=I.classes.map(function(c){return {c:c,sc:score(c.n+" "+c.g,c.n)};}).filter(function(x){return x.sc>=5;}).sort(function(a,b){return b.sc-a.sc;}).slice(0,5).map(function(x){return x.c;});
    var pr=I.products.map(function(p){return {p:p,sc:score(p.t+" "+p.c+" "+p.y,p.y)};}).filter(function(x){return x.sc>0;}).sort(function(a,b){return b.sc-a.sc||a.p.p-b.p.p;}).slice(0,8).map(function(x){return x.p;});
    return {classes:cl,products:pr};
  }
  function rows(r){
    var h="";
    if(r.classes.length) h+='<div class="srch-sec">Licenses</div>'+r.classes.map(function(c){return '<a class="srch-row" href="'+esc(BASE+c.u)+'"><b>'+esc(c.n)+'</b><span>'+c.k+' option'+(c.k===1?"":"s")+' from '+money(c.lo)+'</span></a>';}).join("");
    if(r.products.length) h+='<div class="srch-sec">Products</div>'+r.products.map(function(p){return '<a class="srch-row" href="'+esc(BASE+p.u)+'"><img src="'+esc(p.i)+'" alt="" loading="lazy"><span class="srch-t"><b>'+esc(p.y)+'</b><small>'+esc(p.c)+'</small></span><span class="srch-p">'+money(p.p)+'</span></a>';}).join("");
    return h;
  }
  function render(text){
    if(!text.trim()){res.innerHTML="";return;}
    res.innerHTML=rows(search(text))||'<p class="srch-none">Nothing found for “'+esc(text)+'”. Try a trade, such as roofing, plumber or inspector.</p>';
  }
  function open(){opener=document.activeElement;ov.hidden=false;ov.setAttribute("aria-hidden","false");document.documentElement.classList.add("modal-open");setTimeout(function(){q.focus();},20);ensureIndex(function(){render(q.value);});}
  function close(){ov.hidden=true;ov.setAttribute("aria-hidden","true");document.documentElement.classList.remove("modal-open");if(opener&&opener.focus)opener.focus();}
  var tmr; q.addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(function(){ensureIndex(function(){render(q.value);});},80);});
  q.closest("form").addEventListener("submit",function(e){var first=res.querySelector(".srch-row");if(first){e.preventDefault();location.href=first.href;}});
  document.addEventListener("click",function(e){if(e.target.closest("[data-sopen]")){e.preventDefault();open();}else if(e.target.closest("[data-sclose]")){e.preventDefault();close();}});
  document.addEventListener("keydown",function(e){
    if(e.key==="Escape"&&!ov.hidden){close();return;}
    if(e.key==="/"&&ov.hidden&&!/input|textarea|select/i.test((document.activeElement||{}).tagName||"")){e.preventDefault();open();}
  });
  var sp=document.getElementById("searchPage");
  if(sp){var m=location.search.match(/[?&]q=([^&]*)/);var inp=sp.querySelector("input");inp.value=m?decodeURIComponent(m[1].replace(/\+/g," ")):"";
    function go(){ensureIndex(function(){var out=document.getElementById("searchOut");out.innerHTML=rows(search(inp.value))||(inp.value.trim()?'<p class="srch-none">Nothing found. Try a trade, such as roofing, plumber or inspector.</p>':"");
      document.title=(inp.value.trim()?"Search: "+inp.value+" | ":"Search | ")+((window.SITE||{}).brand||"");});}
    inp.addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(go,80);}); sp.addEventListener("submit",function(e){e.preventDefault();go();history.replaceState(null,"","?q="+encodeURIComponent(inp.value));}); go();}
})();
