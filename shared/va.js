/* Small page behaviour for the listing pages: footer year, one FAQ open at a time. */
(function(){
  "use strict";
  document.querySelectorAll("[data-year]").forEach(function(el){el.textContent=new Date().getFullYear();});
  document.querySelectorAll(".faq details").forEach(function(d){d.addEventListener("toggle",function(){if(d.open)d.parentNode.querySelectorAll("details").forEach(function(o){if(o!==d)o.open=false;});});});
})();
