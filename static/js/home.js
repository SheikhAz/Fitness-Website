document.addEventListener("DOMContentLoaded", () => {
  /* ========= MOBILE MENU ========= */
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const closeMenu = document.getElementById("closeMenu");

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
  }

  /* ========= DJANGO FLASH MESSAGES ========= */
  const messages = document.querySelectorAll(".flash-message");

  messages.forEach((msg, i) => {
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";

    // staggered entrance
    setTimeout(() => {
      msg.style.transition = "all 0.4s ease";
      msg.style.opacity = "1";
      msg.style.transform = "translateY(0)";
    }, i * 150);

    // auto-dismiss after 4 s
    setTimeout(() => removeMessage(msg), 4000 + i * 200);

    const closeBtn = msg.querySelector(".close-btn");
    if (closeBtn) closeBtn.addEventListener("click", () => removeMessage(msg));
  });

  function removeMessage(msg) {
    if (!msg.isConnected) return; // already removed — skip
    msg.style.transition = "all 0.3s ease";
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";
    setTimeout(() => msg.remove(), 300);
  }

  /* ========= HERO STATS ========= */
  function animateCount(el, target) {
    if (!el) return;
    let current = 0;
    const dur = 1400; // total animation ms
    const step = 16; // ~60 fps
    const inc = Math.ceil(target / (dur / step));

    const timer = setInterval(() => {
      current += inc;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current;
    }, step);
  }

  // static counters
  animateCount(document.getElementById("statExercise"), 20);
  animateCount(document.getElementById("statSatisfaction"), 92);

  // dynamic user count from API
  fetch("/api/stats/")
    .then((r) => {
      if (!r.ok) throw new Error("Network response was not ok");
      return r.json();
    })
    .then((data) => {
      const users = data.total_users || 0;
      // show rounded-up double if >= 50, else raw count (minimum 10)
      const display = users < 50 ? users : Math.ceil(users / 10) * 10 * 2;
      animateCount(document.getElementById("statUsers"), display || 10);
    })
    .catch(() => {
      // fallback if API is unavailable
      animateCount(document.getElementById("statUsers"), 10);
    });

  /* ========= SCROLL-TRIGGERED ANIMATIONS ========= */
  // Animate elements with class "hero-animate" when they enter the viewport
  const animatedEls = document.querySelectorAll(".hero-animate");

  if ("IntersectionObserver" in window && animatedEls.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.animationPlayState = "running";
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );

    animatedEls.forEach((el) => {
      el.style.animationPlayState = "paused";
      observer.observe(el);
    });
  }

  /* ========= NAVBAR SCROLL SHADOW ========= */
  // Adds a subtle bottom border to the navbar once the user scrolls
  const navbarEl = document.getElementById("navbar");

  if (navbarEl) {
    window.addEventListener(
      "scroll",
      () => {
        if (window.scrollY > 10) {
          navbarEl.style.borderBottom = "1px solid rgba(249,115,22,0.25)";
        } else {
          navbarEl.style.borderBottom = "";
        }
      },
      { passive: true },
    );
  }

  /* ========= SMOOTH SCROLL FOR ANCHOR LINKS ========= */
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
});

/* ========= FEATURE CARDS TOGGLE ========= */
// Accordion: one card open at a time; clicking the open card closes it
function toggleFeature(card) {
  const isActive = card.classList.contains("active");

  document.querySelectorAll(".feature-card").forEach((c) => {
    c.classList.remove("active");
  });

  if (!isActive) {
    card.classList.add("active");

    // smooth scroll so the opened card is fully visible on small screens
    setTimeout(() => {
      const rect = card.getBoundingClientRect();
      const bottom = rect.bottom + window.scrollY;
      const viewH = window.innerHeight;

      if (rect.bottom > viewH - 20) {
        window.scrollBy({ top: rect.bottom - viewH + 40, behavior: "smooth" });
      }
    }, 460); // wait for CSS transition to finish
  }
}

/* ========= PRICING CARDS TOGGLE ========= */
// Same accordion pattern as feature cards
function togglePricing(card) {
  const isActive = card.classList.contains("active");

  document.querySelectorAll(".pricing-card").forEach((c) => {
    c.classList.remove("active");
  });

  if (!isActive) {
    card.classList.add("active");

    setTimeout(() => {
      const rect = card.getBoundingClientRect();
      if (rect.bottom > window.innerHeight - 20) {
        window.scrollBy({
          top: rect.bottom - window.innerHeight + 40,
          behavior: "smooth",
        });
      }
    }, 460);
  }
}
