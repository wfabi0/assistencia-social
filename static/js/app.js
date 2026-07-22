document.addEventListener('DOMContentLoaded', () => {
  const currentPath = window.location.pathname.replace(/\/$/, '');

  document.querySelectorAll('.sidebar .nav-link').forEach((link) => {
    const href = link.getAttribute('href');
    if (!href || href === '#') {
      return;
    }

    const normalizedHref = href.replace(/\/$/, '');
    if (normalizedHref === currentPath) {
      link.classList.add('active');
    }
  });

  const loginForm = document.querySelector('.login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', () => {
      const submitButton = loginForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('btn-loading');
      }
    });
  }

  const sidebarCollapseEl = document.getElementById('sidebarCollapse');
  if (sidebarCollapseEl) {
    document.querySelectorAll('.sidebar .nav-link').forEach((link) => {
      link.addEventListener('click', () => {
        if (sidebarCollapseEl.classList.contains('show') && typeof bootstrap !== 'undefined') {
          const collapse = bootstrap.Collapse.getOrCreateInstance(sidebarCollapseEl);
          collapse.hide();
        }
      });
    });
  }
});
