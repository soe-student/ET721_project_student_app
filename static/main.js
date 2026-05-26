// ── Flash auto-dismiss ──────────────────────────────────────────────────────
document.querySelectorAll(".flash").forEach(el => {
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity .5s";
    setTimeout(() => el.remove(), 500); }, 4000);
});

// ── Upload drag & drop ──────────────────────────────────────────────────────
const zone = document.querySelector(".upload-zone");
if (zone) {
  const input = zone.querySelector("input[type=file]");
  const label = zone.querySelector(".upload-label");
  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag"));
  zone.addEventListener("drop", e => {
    e.preventDefault(); zone.classList.remove("drag");
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      if (label) label.textContent = e.dataTransfer.files[0].name;
    }
  });
  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    if (input.files.length && label) label.textContent = input.files[0].name;
  });
}

// ── Active nav link ─────────────────────────────────────────────────────────
document.querySelectorAll(".nav-links a").forEach(a => {
  if (a.href === window.location.href) a.classList.add("active");
});

// ── Confirm deletes ─────────────────────────────────────────────────────────
document.querySelectorAll("[data-confirm]").forEach(btn => {
  btn.addEventListener("click", e => {
    if (!confirm(btn.dataset.confirm)) e.preventDefault();
  });
});
