/* JobTrack — main.js */

document.addEventListener("DOMContentLoaded", () => {
  initSidebar();
  initToasts();
  initDeleteModal();
  initDarkMode();
  initFormLoading();
  initNotifications();
  initGlobalSearch();
});

/* --- Sidebar toggle --- */
function initSidebar() {
  const toggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  if (!toggle || !sidebar) return;

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    if (overlay) overlay.classList.toggle("show");
  });
  if (overlay) {
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    });
  }
}

/* --- Auto-dismiss toasts --- */
function initToasts() {
  document.querySelectorAll(".toast-notification").forEach((el, i) => {
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateX(20px)";
      setTimeout(() => el.remove(), 300);
    }, 4500 + i * 300);
  });
}

/* --- Delete confirmation modal --- */
function initDeleteModal() {
  const modal = document.getElementById("deleteModal");
  if (!modal) return;
  window._deleteModal = new bootstrap.Modal(modal);
}

function confirmDelete(actionUrl, label) {
  const form = document.getElementById("deleteForm");
  const target = document.getElementById("deleteTarget");
  if (!form || !target) return;
  form.action = actionUrl;
  target.textContent = label;
  window._deleteModal.show();
}

/* --- Dark mode --- */
function initDarkMode() {
  const btn = document.getElementById("darkModeToggle");
  const saved = localStorage.getItem("theme");
  if (saved === "dark") document.body.classList.add("dark-mode");
  if (btn) {
    updateDarkBtn(btn);
    btn.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      const isDark = document.body.classList.contains("dark-mode");
      localStorage.setItem("theme", isDark ? "dark" : "light");
      updateDarkBtn(btn);
    });
  }
}

function updateDarkBtn(btn) {
  const isDark = document.body.classList.contains("dark-mode");
  btn.innerHTML = isDark ? '<i class="bi bi-sun"></i>' : '<i class="bi bi-moon"></i>';
  btn.title = isDark ? "Switch to light mode" : "Switch to dark mode";
}

/* --- Disable submit button while submitting --- */
function initFormLoading() {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn && !btn.dataset.noload) {
        btn.disabled = true;
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving…';
        setTimeout(() => { btn.disabled = false; btn.innerHTML = orig; }, 8000);
      }
    });
  });
}

/* --- Password visibility toggle --- */
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isText = input.type === "text";
  input.type = isText ? "password" : "text";
  btn.innerHTML = isText ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
}

/* --- Live notifications bell --- */
function initNotifications() {
  const btn = document.getElementById("notifBtn");
  const dropdown = document.getElementById("notifDropdown");
  const badge = document.getElementById("notifBadge");
  const list = document.getElementById("notifList");
  if (!btn) return;

  // Fetch notifications from API
  function fetchNotifications() {
    fetch("/api/notifications")
      .then(r => r.json())
      .then(data => {
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.classList.remove("d-none");
        } else {
          badge.classList.add("d-none");
        }

        if (data.items.length === 0) {
          list.innerHTML = '<div class="notif-empty"><i class="bi bi-check-circle"></i> All caught up!</div>';
        } else {
          list.innerHTML = data.items.map(n => `
            <a href="${n.url}" class="notif-item notif-${n.type}">
              <div class="notif-icon">
                <i class="bi ${n.type === 'interview' ? 'bi-camera-video' : 'bi-bell'}"></i>
              </div>
              <div>
                <div class="notif-title">${n.title}</div>
                <div class="notif-body">${n.body}</div>
              </div>
            </a>
          `).join("");
        }
      })
      .catch(() => {});
  }

  fetchNotifications();

  // Toggle dropdown
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("d-none");
  });

  document.addEventListener("click", (e) => {
    if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add("d-none");
    }
  });
}

/* --- Global search keyboard shortcut (/) --- */
function initGlobalSearch() {
  const input = document.getElementById("globalSearch");
  if (!input) return;

  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      input.focus();
      input.select();
    }
    if (e.key === "Escape" && document.activeElement === input) {
      input.blur();
    }
  });
}
