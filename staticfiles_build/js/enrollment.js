/* ── Close all dropdowns ── */
function closeAll() {
  ["gender", "plan", "trainer"].forEach((id) => {
    document.getElementById(id + "Dropdown")?.classList.remove("open");
    document.getElementById(id + "Btn")?.classList.remove("open");
  });
}

/* ── Toggle dropdown ── */
function toggleDropdown(id) {
  const menu = document.getElementById(id + "Dropdown");
  const btn = document.getElementById(id + "Btn");

  const isOpen = menu.classList.contains("open");
  closeAll();

  if (!isOpen) {
    menu.classList.add("open");
    btn.classList.add("open");
  }
}

/* ── Outside click ── */
document.addEventListener("click", function (e) {
  if (!e.target.closest(".dropdown-wrap")) closeAll();
});

/* ── DOM Loaded ── */
document.addEventListener("DOMContentLoaded", () => {
  /* ===== BUTTON TOGGLE ===== */
  document.getElementById("genderBtn").onclick = () => toggleDropdown("gender");

  document.getElementById("planBtn").onclick = () => toggleDropdown("plan");

  document.getElementById("trainerBtn").onclick = () =>
    toggleDropdown("trainer");

  /* ===== GENDER SELECT ===== */
  document
    .querySelectorAll("#genderDropdown .dropdown-item")
    .forEach((item) => {
      item.addEventListener("click", () => {
        const val = item.dataset.value;

        document.getElementById("selectedGender").textContent =
          val === "M" ? "Male" : "Female";

        document
          .getElementById("selectedGender")
          .classList.remove("placeholder");

        document.getElementById("genderInput").value = val;

        closeAll();
      });
    });
  /* ===== SUBMIT LOADING ===== */
  document.getElementById("enrollForm").addEventListener("submit", function () {
    const btn = document.getElementById("enrollBtn");

    if (this.checkValidity()) {
      btn.textContent = "Processing...";
      btn.disabled = true;
    }
  });
});
function selectPlan(id, name, price) {
  console.log("Selected:", id, name, price); // debug

  document.getElementById("selectedPlan").innerText = name + " - ₹" + price;

  document.getElementById("planInput").value = id;

  closeAll(); // better than hidden class
}
function selectTrainer(id, name) {
  document.getElementById("selectedTrainer").innerText = name;
  document.getElementById("trainerInput").value = id;
  closeAll();
}
