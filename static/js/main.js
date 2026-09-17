/* ==========================================================================
   Turkiy yozma meros — 2026 · sayt skriptlari
   ========================================================================== */
(function () {
  "use strict";

  // --- Mobil menyu --------------------------------------------------------
  var burger = document.getElementById("burger");
  var nav = document.getElementById("nav");

  if (burger && nav) {
    burger.addEventListener("click", function () {
      var ochiq = nav.classList.toggle("ochiq");
      burger.classList.toggle("ochiq", ochiq);
      burger.setAttribute("aria-expanded", ochiq ? "true" : "false");
    });

    // Havola bosilganda menyuni yopish
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("ochiq");
        burger.classList.remove("ochiq");
        burger.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("ochiq")) {
        burger.click();
      }
    });
  }

  // --- Sahifa surilganda sarlavhaga soya ----------------------------------
  var header = document.getElementById("header");
  if (header) {
    var surilishni_tekshir = function () {
      header.classList.toggle("header--surilgan", window.scrollY > 10);
    };
    surilishni_tekshir();
    window.addEventListener("scroll", surilishni_tekshir, { passive: true });
  }

  // --- Flash xabarlar -----------------------------------------------------
  document.querySelectorAll(".flash").forEach(function (flash) {
    var yopish = function () {
      flash.style.transition = "opacity .3s, transform .3s";
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      setTimeout(function () { flash.remove(); }, 300);
    };

    var tugma = flash.querySelector(".flash__yopish");
    if (tugma) tugma.addEventListener("click", yopish);

    // Muvaffaqiyat xabarlari o'zi yo'qoladi, xatolar qoladi
    if (flash.classList.contains("flash--muvaffaqiyat")) {
      setTimeout(yopish, 6000);
    }
  });

  // --- Teskari hisoblagich ------------------------------------------------
  var hisoblagich = document.getElementById("hisoblagich");
  if (hisoblagich) {
    var sana = new Date(hisoblagich.dataset.sana);

    if (!isNaN(sana.getTime())) {
      var kataklar = {
        kun: document.getElementById("kun"),
        soat: document.getElementById("soat"),
        daqiqa: document.getElementById("daqiqa"),
        soniya: document.getElementById("soniya")
      };

      var ikki_xona = function (son) {
        return son < 10 ? "0" + son : String(son);
      };

      var yangila = function () {
        var farq = sana.getTime() - Date.now();

        if (farq <= 0) {
          hisoblagich.className = "hisoblagich--tugadi";
          hisoblagich.textContent = hisoblagich.dataset.tugadi || "";
          clearInterval(oraliq);
          return;
        }

        var soniya_jami = Math.floor(farq / 1000);
        kataklar.kun.textContent = Math.floor(soniya_jami / 86400);
        kataklar.soat.textContent = ikki_xona(Math.floor(soniya_jami / 3600) % 24);
        kataklar.daqiqa.textContent = ikki_xona(Math.floor(soniya_jami / 60) % 60);
        kataklar.soniya.textContent = ikki_xona(soniya_jami % 60);
      };

      var oraliq = setInterval(yangila, 1000);
      yangila();
    }
  }

  // --- Formani ikki marta yuborishdan saqlash -----------------------------
  var yuborilmoqda = document.body.dataset.yuborilmoqda || "...";

  document.querySelectorAll("form").forEach(function (forma) {
    forma.addEventListener("submit", function () {
      var tugma = forma.querySelector('button[type="submit"], button:not([type])');
      if (!tugma || tugma.disabled) return;

      // Brauzer forma ma'lumotini yig'ib bo'lgach ishga tushadi
      setTimeout(function () {
        tugma.disabled = true;
        if (!tugma.classList.contains("mayda-tugma")) {
          tugma.textContent = yuborilmoqda;
        }
      }, 0);
    });
  });

  // --- Ichki havolalar bo'yicha silliq siljish ----------------------------
  document.querySelectorAll('a[href^="#"]').forEach(function (havola) {
    havola.addEventListener("click", function (e) {
      var id = havola.getAttribute("href");
      if (id.length < 2) return;

      var nishon = document.querySelector(id);
      if (!nishon) return;

      e.preventDefault();
      nishon.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
})();
