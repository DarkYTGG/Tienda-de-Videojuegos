/**
 * PixelVault — Interactive Frontend JavaScript
 * Handles reactive cart actions, AJAX offcanvas drawer, live toasts, and key copying.
 */

document.addEventListener("DOMContentLoaded", () => {
  initToasts();
  initCopyKeyButtons();
});

// -------------------------------------------------------------
// Interactive Cart Operations (AJAX)
// -------------------------------------------------------------
async function addToCart(gameId, buttonEl) {
  try {
    const originalHtml = buttonEl ? buttonEl.innerHTML : "";
    if (buttonEl) {
      buttonEl.disabled = true;
      buttonEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Añadiendo...';
    }

    const response = await fetch(`/api/cart/add/${gameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    const data = await response.json();

    if (data.success) {
      // 1. Update all navbar cart badges
      updateNavCartCount(data.cart_count);

      // 2. Update button UI
      if (buttonEl) {
        buttonEl.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> En Carrito';
        buttonEl.classList.add("in-cart");
      }

      // 3. Show Toast Feedback
      showToast(data.message, "success");

      // 4. Refresh and Open Offcanvas Cart Drawer
      refreshAndOpenCartDrawer();
    } else {
      showToast(data.message || "No se pudo añadir al carrito", "warning");
      if (buttonEl) {
        buttonEl.disabled = false;
        buttonEl.innerHTML = originalHtml;
      }
    }
  } catch (error) {
    console.error("Cart error:", error);
    showToast("Error de conexión al agregar el videojuego.", "danger");
  }
}

async function removeFromCart(gameId, isPage = false) {
  try {
    const response = await fetch(`/api/cart/remove/${gameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const data = await response.json();

    if (data.success) {
      updateNavCartCount(data.cart_count);
      showToast("Videojuego eliminado del carrito.", "info");

      if (isPage) {
        // If on /cart or /checkout page, reload to recompute totals cleanly
        window.location.reload();
      } else {
        refreshCartDrawer();
      }
    }
  } catch (err) {
    console.error("Remove cart error:", err);
  }
}

function updateNavCartCount(count) {
  const badges = document.querySelectorAll(".badge-cart-count");
  badges.forEach(b => {
    b.textContent = count;
    b.style.transform = "scale(1.3)";
    setTimeout(() => { b.style.transform = "scale(1)"; }, 250);
  });
}

// -------------------------------------------------------------
// Offcanvas Drawer Population
// -------------------------------------------------------------
async function refreshAndOpenCartDrawer() {
  await refreshCartDrawer();
  const drawerEl = document.getElementById("cartOffcanvas");
  if (drawerEl && typeof bootstrap !== "undefined") {
    const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawerEl);
    bsOffcanvas.show();
  }
}

async function refreshCartDrawer() {
  const container = document.getElementById("cartDrawerItems");
  const subtotalEl = document.getElementById("cartDrawerSubtotal");
  const totalEl = document.getElementById("cartDrawerTotal");
  const checkoutBtn = document.getElementById("cartDrawerCheckoutBtn");

  if (!container) return;

  try {
    const res = await fetch("/api/cart/state");
    const data = await res.json();

    if (data.items.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5">
          <i class="bi bi-cart-x fs-1 text-secondary opacity-50 mb-3 d-block"></i>
          <h6 class="text-white">Tu carrito está vacío</h6>
          <p class="text-muted small">Explora nuestro catálogo y agrega tus títulos favoritos.</p>
          <a href="/catalog" class="btn btn-sm btn-outline-pixel mt-2">Ir a Catálogo</a>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = "$0.00 USD";
      if (totalEl) totalEl.textContent = "$0.00 USD";
      if (checkoutBtn) checkoutBtn.classList.add("disabled");
    } else {
      let html = "";
      data.items.forEach(item => {
        html += `
          <div class="cart-drawer-item">
            <img src="${item.cover_image}" alt="${item.title}" class="cart-drawer-thumb">
            <div class="flex-grow-1 min-w-0">
              <h6 class="text-white text-truncate mb-0 fs-6">${item.title}</h6>
              <div class="d-flex align-items-center gap-2 mt-1">
                <span class="badge-genre" style="font-size:0.7rem;">${item.genre}</span>
                <span class="text-white fw-bold small">${item.price === 0 ? 'Gratis' : '$' + item.price.toFixed(2) + ' USD'}</span>
              </div>
            </div>
            <button class="btn btn-sm text-danger" onclick="removeFromCart('${item.id}', false)" title="Eliminar">
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        `;
      });
      container.innerHTML = html;
      if (subtotalEl) subtotalEl.textContent = `$${data.subtotal.toFixed(2)} USD`;
      if (totalEl) totalEl.textContent = `$${data.total.toFixed(2)} USD`;
      if (checkoutBtn) checkoutBtn.classList.remove("disabled");
    }
  } catch (err) {
    console.error("Failed to refresh cart drawer:", err);
  }
}

// -------------------------------------------------------------
// Toast Notifications
// -------------------------------------------------------------
function showToast(message, type = "info") {
  const toastContainer = document.getElementById("toastContainer");
  if (!toastContainer) return;

  const bgClass = {
    success: "bg-success text-white",
    warning: "bg-warning text-dark",
    danger: "bg-danger text-white",
    info: "bg-dark text-white border border-secondary"
  }[type] || "bg-dark text-white";

  const iconClass = {
    success: "bi-check-circle-fill",
    warning: "bi-exclamation-triangle-fill",
    danger: "bi-x-circle-fill",
    info: "bi-info-circle-fill"
  }[type] || "bi-info-circle-fill";

  const toastId = "toast_" + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${iconClass} fs-5"></i>
          <span class="fw-medium">${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML("beforeend", toastHtml);
  const toastElement = document.getElementById(toastId);
  const bsToast = new bootstrap.Toast(toastElement, { delay: 3500 });
  bsToast.show();

  toastElement.addEventListener("hidden.bs.toast", () => {
    toastElement.remove();
  });
}

function initToasts() {
  if (!document.getElementById("toastContainer")) {
    const container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    container.style.zIndex = "1090";
    document.body.appendChild(container);
  }
}

// -------------------------------------------------------------
// Digital Activation Key Copying
// -------------------------------------------------------------
function initCopyKeyButtons() {
  document.querySelectorAll(".btn-copy-key").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-key");
      if (key) {
        navigator.clipboard.writeText(key).then(() => {
          const original = btn.innerHTML;
          btn.innerHTML = '<i class="bi bi-check2"></i> ¡Copiado!';
          btn.classList.add("bg-success", "text-white");
          setTimeout(() => {
            btn.innerHTML = original;
            btn.classList.remove("bg-success", "text-white");
          }, 2000);
          showToast(`Clave digital ${key} copiada al portapapeles.`, "success");
        });
      }
    });
  });
}
