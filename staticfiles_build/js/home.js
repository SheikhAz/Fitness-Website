document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const closeMenu = document.getElementById("closeMenu");

  /* ========= MOBILE MENU ========= */
  if (menuBtn && mobileMenu && closeMenu) {
    mobileMenu.classList.remove("active");

    // Open menu
    menuBtn.addEventListener("click", () => {
      mobileMenu.classList.add("active");
    });

    // Close from X button
    closeMenu.addEventListener("click", () => {
      mobileMenu.classList.remove("active");
    });

    // Close when clicking outside (overlay)
    mobileMenu.addEventListener("click", (e) => {
      if (e.target === mobileMenu) {
        mobileMenu.classList.remove("active");
      }
    });

    // Close when clicking ANY link/button inside menu
    const menuItems = mobileMenu.querySelectorAll("a, button");
    menuItems.forEach((item) => {
      item.addEventListener("click", () => {
        mobileMenu.classList.remove("active");
      });
    });
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
    // Entry animation
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";

    setTimeout(() => {
      msg.style.transition = "all 0.4s ease";
      msg.style.opacity = "1";
      msg.style.transform = "translateY(0)";
    }, i * 150);

    // Auto remove
    setTimeout(
      () => {
        removeMessage(msg);
      },
      4000 + i * 200,
    );

    // Close button
    const closeBtn = msg.querySelector(".close-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        removeMessage(msg);
      });
    }
  });

  function removeMessage(msg) {
    msg.style.transition = "all 0.3s ease";
    msg.style.opacity = "0";
    msg.style.transform = "translateY(-10px)";

    setTimeout(() => {
      msg.remove();
    }, 300);
  }
});

/* ========= FEATURE TOGGLE ========= */
function toggleFeature(card) {
  const allCards = document.querySelectorAll(".feature-card");

  allCards.forEach((c) => {
    if (c !== card) {
      c.classList.remove("active");
    }
  });

  card.classList.toggle("active");
}

/* ========= PRICING TOGGLE ========= */
function togglePricing(card) {
  const allCards = document.querySelectorAll(".pricing-card");

  allCards.forEach((c) => {
    if (c !== card) {
      c.classList.remove("active");
    }
  });

  card.classList.toggle("active");
}
