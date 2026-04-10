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

/* ── Outside click closes dropdowns ── */
document.addEventListener("click", function (e) {
  if (!e.target.closest(".dropdown-wrap")) closeAll();
});

/* ── Plan select ── */
function selectPlan(id, name, price) {
  const label = document.getElementById("selectedPlan");
  label.innerText = name + " - ₹" + price;
  label.classList.remove("placeholder");
  document.getElementById("planInput").value = id;
  closeAll();
}

/* ── Trainer select ── */
function selectTrainer(id, name) {
  const label = document.getElementById("selectedTrainer");
  label.innerText = name;
  label.classList.remove("placeholder");
  document.getElementById("trainerInput").value = id;
  closeAll();
}

/* ── DOM Ready ── */
document.addEventListener("DOMContentLoaded", () => {
  /* ── Dropdown button bindings ── */
  document.getElementById("genderBtn").onclick = () => toggleDropdown("gender");
  document.getElementById("planBtn").onclick = () => toggleDropdown("plan");
  document.getElementById("trainerBtn").onclick = () =>
    toggleDropdown("trainer");

  /* ── Gender select ── */
  document
    .querySelectorAll("#genderDropdown .dropdown-item")
    .forEach((item) => {
      item.addEventListener("click", () => {
        const val = item.dataset.value;
        const label = document.getElementById("selectedGender");

        label.textContent = val === "M" ? "Male" : "Female";
        label.classList.remove("placeholder");
        document.getElementById("genderInput").value = val;

        closeAll();
      });
    });

      const dobDisplay = document.getElementById("dobDisplay");
      const dobInput = document.getElementById("dobInput");

      dobInput.addEventListener("change", () => {
        if (dobInput.value) {
          const [y, m, d] = dobInput.value.split("-");
          dobDisplay.value = `${d}/${m}/${y}`;
          dobDisplay.classList.add("has-value");
        } else {
          dobDisplay.value = "";
          dobDisplay.classList.remove("has-value");
        }
      });

  /* ── Submit loading state ── */
  document.getElementById("enrollForm").addEventListener("submit", function () {
    const btn = document.getElementById("enrollBtn");
    if (this.checkValidity()) {
      btn.textContent = "Processing...";
      btn.disabled = true;
    }
  });
});
