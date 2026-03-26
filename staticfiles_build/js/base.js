document.addEventListener("DOMContentLoaded", () => {
  const popupMenu = document.getElementById("popupMenu");
  const closeMenu = document.getElementById("closeMenu");

  // Example trigger (you can connect hamburger button)
  document.addEventListener("keydown", (e) => {
    if (e.key === "m") {
      popupMenu.classList.add("active");
    }
  });

  // Close menu
  closeMenu.addEventListener("click", () => {
    popupMenu.classList.remove("active");
  });

  // Close on outside click
  window.addEventListener("click", (e) => {
    if (e.target === popupMenu) {
      popupMenu.classList.remove("active");
    }
  });
});
