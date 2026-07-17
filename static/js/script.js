/* ---------------------------------------------------------------------
   Expense Tracker - shared front-end behaviour:
   - Sidebar toggle for mobile
   - Dark mode toggle (persisted via a cookie, since we cannot rely on
     localStorage/sessionStorage in every hosting context)
   - AJAX-free "confirm" helper for delete buttons
   - Loading spinner shown while forms submit
--------------------------------------------------------------------- */

function etSetCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
}

function etGetCookie(name) {
    const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
    return match ? match[2] : null;
}

document.addEventListener('DOMContentLoaded', function () {
    // --- Sidebar toggle (mobile) ---
    const sidebar = document.getElementById('etSidebar');
    const backdrop = document.getElementById('etSidebarBackdrop');
    const toggleBtn = document.getElementById('etSidebarToggle');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            if (backdrop) backdrop.classList.toggle('show');
        });
    }
    if (backdrop) {
        backdrop.addEventListener('click', function () {
            sidebar.classList.remove('show');
            backdrop.classList.remove('show');
        });
    }

    // --- Dark mode toggle ---
    const darkToggle = document.getElementById('etDarkModeToggle');
    const savedTheme = etGetCookie('et_theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    if (darkToggle) {
        darkToggle.checked = savedTheme === 'dark';
        darkToggle.addEventListener('change', function () {
            const theme = darkToggle.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-bs-theme', theme);
            etSetCookie('et_theme', theme, 365);
        });
    }

    // --- Delete confirmation modal trigger ---
    document.querySelectorAll('.et-delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const confirmed = window.confirm('Are you sure you want to delete this transaction? This cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            } else {
                showEtSpinner();
            }
        });
    });

    // --- Show spinner on any form submit that opts in ---
    document.querySelectorAll('form.et-loading-form').forEach(function (form) {
        form.addEventListener('submit', function () {
            showEtSpinner();
        });
    });

    // --- Auto-update category dropdown options based on transaction type ---
    const typeSelect = document.getElementById('id_transaction_type');
    const categorySelect = document.getElementById('id_category');
    if (typeSelect && categorySelect && window.etCategoriesByType) {
        const applyFilter = function () {
            const type = typeSelect.value;
            const options = window.etCategoriesByType[type] || [];
            const currentValue = categorySelect.value;
            categorySelect.innerHTML = '';
            options.forEach(function (opt) {
                const el = document.createElement('option');
                el.value = opt.id;
                el.textContent = opt.name;
                if (String(opt.id) === currentValue) el.selected = true;
                categorySelect.appendChild(el);
            });
        };
        typeSelect.addEventListener('change', applyFilter);
    }
});

function showEtSpinner() {
    const overlay = document.getElementById('etSpinnerOverlay');
    if (overlay) overlay.classList.remove('d-none');
}
