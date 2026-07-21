/* Credify Capital - scripts.js */

(function () {
  function initMobileMenu() {
    var menuBtn = document.getElementById('mobile-menu-btn');
    var menuPanel = document.getElementById('mobile-menu-panel');
    var menuIcon = document.getElementById('mobile-menu-icon');
    if (menuBtn && menuPanel) {
      // Avoid adding multiple listeners if the script is loaded multiple times or already configured
      if (menuBtn.dataset.menuInitialized) return;
      menuBtn.dataset.menuInitialized = "true";

      menuBtn.addEventListener('click', function () {
        var isOpen = !menuPanel.classList.contains('hidden');
        menuPanel.classList.toggle('hidden');
        menuBtn.setAttribute('aria-expanded', String(!isOpen));
        if (menuIcon) {
          menuIcon.textContent = isOpen ? 'menu' : 'close';
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileMenu);
  } else {
    initMobileMenu();
  }
})();
