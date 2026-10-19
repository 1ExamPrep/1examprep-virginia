/* Product page behaviour: variant picker updates price + Buy link; gallery thumbnails. */
(function(){
  "use strict";
  var P=window.PRODUCT||{}, STORE=(window.SITE||{}).storeUrl||"https://1examprep.com";
  function money(v){v=Number(v);return "$"+(v%1?v.toFixed(2):String(v)).replace(/\B(?=(\d{3})+(?!\d))/g,",");}
  function cartUrl(id){return STORE+"/cart/"+id+":1"+((window.SITE||{}).cartTag||"");}
  var form=document.getElementById("variants"), now=document.getElementById("pNow"), was=document.getElementById("pWas"), save=document.getElementById("pSave");
  function apply(){
    var r=form&&form.querySelector('input[name="v"]:checked'); if(!r) return;
    var v=(P.variants||[]).filter(function(x){return String(x.id)===r.value;})[0]; if(!v) return;
    now.textContent=money(v.price); document.getElementById("sPrice").textContent=money(v.price);
    var c=parseFloat(v.compareAt||0), n=parseFloat(v.price);
    if(was){was.textContent=c>n?money(c):""; was.hidden=!(c>n);}
    if(save){save.textContent=c>n?("Save "+Math.round((c-n)/c*100)+"%"):""; save.hidden=!(c>n);}
    ["buyBtn","sBuy"].forEach(function(id){var b=document.getElementById(id);if(b)b.href=cartUrl(v.id);});
    var nb=document.querySelector(".nav .btn-buy"); if(nb) nb.href=cartUrl(v.id);
  }
  if(form){form.addEventListener("change",apply);apply();}
  var thumbs=document.getElementById("gThumbs"), main=document.getElementById("gMain");
  if(thumbs&&main){thumbs.addEventListener("click",function(e){var b=e.target.closest("[data-src]");if(!b)return;main.src=b.getAttribute("data-src");thumbs.querySelectorAll("[data-src]").forEach(function(x){x.classList.toggle("on",x===b);});});}
  document.querySelectorAll("[data-year]").forEach(function(el){el.textContent=new Date().getFullYear();});
  document.querySelectorAll(".faq details").forEach(function(d){d.addEventListener("toggle",function(){if(d.open)d.parentNode.querySelectorAll("details").forEach(function(o){if(o!==d)o.open=false;});});});
})();
