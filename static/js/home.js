document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const closeMenu = document.getElementById("closeMenu");

  /* ========= MOBILE MENU ========= */
  if (menuBtn && mobileMenu && closeMenu) {
    mobileMenu.classList.remove("active");

    menuBtn.addEventListener("click", () => mobileMenu.classList.add("active"));
    closeMenu.addEventListener("click", () =>
      mobileMenu.classList.remove("active"),
    );

    mobileMenu.addEventListener("click", (e) => {
      if (e.target === mobileMenu) mobileMenu.classList.remove("active");
    });

    mobileMenu.querySelectorAll("a, button").forEach((item) => {
      item.addEventListener("click", () =>
        mobileMenu.classList.remove("active"),
      );
    });
  }

  /* ========= NOTIFICATION BAR ========= */
  const notifBar = document.getElementById("notifBar");
  const notifClose = document.getElementById("notifClose");
  const navbar = document.getElementById("navbar");

  if (notifBar && notifClose && navbar) {
    notifClose.addEventListener("click", () => {
      notifBar.classList.add("hidden");
      navbar.classList.add("notif-hidden");
    });

    if (sessionStorage.getItem("notifDismissed") === "1") {
      notifBar.classList.add("hidden");
      navbar.classList.add("notif-hidden");
    }
  }

  /* ========= DJANGO FLASH MESSAGES ========= */
  const messages = document.querySelectorAll(".flash-message");

  messages.forEach((msg, i) => {
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";

    setTimeout(() => {
      msg.style.transition = "all 0.4s ease";
      msg.style.opacity = "1";
      msg.style.transform = "translateY(0)";
    }, i * 150);

    setTimeout(() => removeMessage(msg), 4000 + i * 200);

    const closeBtn = msg.querySelector(".close-btn");
    if (closeBtn) closeBtn.addEventListener("click", () => removeMessage(msg));
  });

  function removeMessage(msg) {
    msg.style.transition = "all 0.3s ease";
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";
    setTimeout(() => msg.remove(), 300);
  }

  /* ========= HERO STATS ========= */
  function animateCount(el, target) {
    if (!el) return;
    let start = 0;
    const dur = 1400;
    const step = 16;
    const inc = Math.ceil(target / (dur / step));
    const t = setInterval(() => {
      start += inc;
      if (start >= target) {
        start = target;
        clearInterval(t);
      }
      el.textContent = start;
    }, step);
  }

  animateCount(document.getElementById("statExercise"), 20);
  animateCount(document.getElementById("statSatisfaction"), 92);

  fetch("/api/stats/")
    .then((r) => r.json())
    .then((data) => {
      const users = data.total_users || 0;
      const display = users < 50 ? users : Math.ceil(users / 10) * 10 * 2;
      animateCount(document.getElementById("statUsers"), display || 10);
    })
    .catch(() => {
      const el = document.getElementById("statUsers");
      if (el) animateCount(el, 10);
    });
});

/* ========= FEATURE TOGGLE ========= */
function toggleFeature(card) {
  document.querySelectorAll(".feature-card").forEach((c) => {
    if (c !== card) c.classList.remove("active");
  });
  card.classList.toggle("active");
}

/* ========= PRICING TOGGLE ========= */
function togglePricing(card) {
  document.querySelectorAll(".pricing-card").forEach((c) => {
    if (c !== card) c.classList.remove("active");
  });
  card.classList.toggle("active");
}
