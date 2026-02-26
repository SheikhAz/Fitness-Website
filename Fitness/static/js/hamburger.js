document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const popupMenu = document.getElementById("popupMenu");
  const closeBtn = document.getElementById("closeMenu");
  const links = popupMenu.querySelectorAll("a");

  function openMenu() {
    popupMenu.classList.remove(
      "opacity-0",
      "-translate-y-20",
      "pointer-events-none",
    );

    popupMenu.classList.add(
      "opacity-100",
      "translate-y-24",
      "pointer-events-auto",
    );
  }

  function closeMenu() {
    popupMenu.classList.add(
      "opacity-0",
      "-translate-y-20",
      "pointer-events-none",
    );

    popupMenu.classList.remove(
      "opacity-100",
      "translate-y-24",
      "pointer-events-auto",
    );
  }

  menuBtn.addEventListener("click", openMenu);
  closeBtn.addEventListener("click", closeMenu);

  // close when link clicked
  links.forEach((link) => {
    link.addEventListener("click", closeMenu);
  });
});
