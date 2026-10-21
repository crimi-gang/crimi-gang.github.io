const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#main-nav");
function closeMenu() {
  navigation?.classList.remove("open");
  menuButton?.setAttribute("aria-expanded", "false");
  menuButton?.setAttribute("aria-label", "Apri menu");
}
menuButton?.addEventListener("click", () => {
  const open = menuButton.getAttribute("aria-expanded") !== "true";
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute("aria-label", open ? "Chiudi menu" : "Apri menu");
  navigation.classList.toggle("open", open);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && navigation?.classList.contains("open")) {
    closeMenu();
    menuButton.focus();
  }
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".site-header")) closeMenu();
});
navigation?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});
window.matchMedia("(min-width: 761px)").addEventListener("change", closeMenu);

document
  .querySelector("[data-copy-email]")
  ?.addEventListener("click", async () => {
    const status = document.querySelector(".copy-status");
    try {
      await navigator.clipboard.writeText("crimisupport@gmail.com");
      status.textContent = "Indirizzo email copiato!";
    } catch {
      status.textContent =
        "Puoi copiare questo indirizzo: crimisupport@gmail.com";
    }
  });

const dialog = document.querySelector(".lightbox");
if (dialog && typeof dialog.showModal === "function") {
  let trigger;
  const close = () => dialog.close();
  document.querySelectorAll("[data-zoom]").forEach((button) => {
    button.addEventListener("click", () => {
      trigger = button;
      const source = button.closest("figure").querySelector("img");
      const image = dialog.querySelector("img");
      image.src = source.dataset.fullSrc || source.currentSrc || source.src;
      image.alt = source.alt;
      dialog.querySelector("p").textContent = button
        .closest("figure")
        .querySelector("figcaption").textContent;
      dialog.showModal();
      document.body.classList.add("modal-open");
    });
    button.hidden = false;
  });
  dialog.querySelector(".lightbox-close").addEventListener("click", close);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      const box = dialog.getBoundingClientRect();
      if (
        event.clientX < box.left ||
        event.clientX > box.right ||
        event.clientY < box.top ||
        event.clientY > box.bottom
      )
        close();
    }
  });
  dialog.addEventListener("close", () => {
    document.body.classList.remove("modal-open");
    dialog.querySelector("img").removeAttribute("src");
    trigger?.focus();
  });
}
