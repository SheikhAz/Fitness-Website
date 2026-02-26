function toggleFeature(card) {
  const desc = card.querySelector(".feature-desc");

  // close others
  document.querySelectorAll(".feature-desc").forEach((el) => {
    if (el !== desc) {
      el.style.maxHeight = null;
      el.style.opacity = 0;
    }
  });

  // toggle clicked
  if (desc.style.maxHeight) {
    desc.style.maxHeight = null;
    desc.style.opacity = 0;
  } else {
    desc.style.maxHeight = desc.scrollHeight + "px";
    desc.style.opacity = 1;
  }
}
