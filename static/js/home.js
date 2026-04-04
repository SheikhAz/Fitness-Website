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
      // Collapse the bar
      notifBar.classList.add("hidden");
      // Shift navbar up so it sits right below topbar
      navbar.classList.add("notif-hidden");
    });

    // Restore dismissed state on page reload
    if (sessionStorage.getItem("notifDismissed") === "1") {
      notifBar.classList.add("hidden");
      navbar.classList.add("notif-hidden");
    }
  }

  /* ========= REVIEW SLIDER ========= */
  let index = 0;
  const reviews = document.getElementById("reviews");
  const totalSlides = document.querySelectorAll(".review").length;

  if (reviews && totalSlides > 0) {
    setInterval(() => {
      index = (index + 1) % totalSlides;
      reviews.style.transform = `translateX(-${index * 100}%)`;
    }, 4000);
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
