/* FORMA тема — мобильное меню */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var burger = document.getElementById("burger");
    var links = document.querySelector(".nav-links");
    if (burger && links) {
      burger.addEventListener("click", function () { links.classList.toggle("open"); });
    }
  });
})();
