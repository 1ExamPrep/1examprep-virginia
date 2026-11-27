/* Small page behaviour for the listing pages: footer year, one FAQ open at a time. */
(function(){
  "use strict";
  document.querySelectorAll("[data-year]").forEach(function(el){el.textContent=new Date().getFullYear();});
  document.querySelectorAll(".faq details").forEach(function(d){d.addEventListener("toggle",function(){if(d.open)d.parentNode.querySelectorAll("details").forEach(function(o){if(o!==d)o.open=false;});});});
})();

/* reviews page widgets (Google reviews via app.1examprep.com and Shopper Approved).
   The iframes and scripts are added here so the served HTML has no iframe or body script. */
(function () {
  var d = document, boxes = d.querySelectorAll(".reviews-embed");
  if (!boxes.length) return;
  function addScript(src) {
    if (d.querySelector('script[src="' + src + '"]')) return;
    var s = d.createElement("script"); s.src = src; s.type = "text/javascript"; s.async = true;
    (d.head || d.body).appendChild(s);
  }
  var lcLoaded = false;
  for (var i = 0; i < boxes.length; i++) {
    var b = boxes[i], kind = b.getAttribute("data-kind");
    if (kind === "google") {
      var f = d.createElement("iframe");
      f.className = "lc_reviews_widget";
      f.src = b.getAttribute("data-src");
      f.title = b.getAttribute("data-title") || "Customer reviews";
      f.setAttribute("frameborder", "0");
      f.setAttribute("scrolling", "no");
      f.setAttribute("loading", "lazy");
      f.style.minWidth = "100%"; f.style.width = "100%"; f.style.border = "0";
      b.innerHTML = ""; b.appendChild(f);
      lcLoaded = true;
    } else if (kind === "shopperapproved") {
      var w = d.createElement("div");
      w.id = b.getAttribute("data-wrapper"); w.className = "SA__wrapper"; w.setAttribute("lang", "en");
      b.innerHTML = ""; b.appendChild(w);
      window.sa_interval = 5000;
      if (typeof window.shopper_first === "undefined") addScript(b.getAttribute("data-src"));
    }
  }
  if (lcLoaded) addScript("https://app.1examprep.com/reputation/assets/review-widget.js");
})();
