// Resolve paths dynamically based on current folder depth
export function getPath(target) {
  const path = window.location.pathname;
  let prefix = './';
  
  if (path.includes('/pages/customer/') || path.includes('/pages/provider/') || path.includes('/pages/shared/') || path.includes('/pages/auth/')) {
    prefix = '../../';
  }
  return prefix + target;
}

// Initialize common Header
export function initHeader(title = '', showBack = false) {
  const headerContainer = document.getElementById('header-container');
  if (!headerContainer) return;
  
  let backBtnHtml = '';
  if (showBack) {
    backBtnHtml = `
      <button class="header-action" onclick="history.back()" aria-label="Go Back">
        <span style="font-size: 20px; font-weight: bold; line-height: 1;">←</span>
      </button>
    `;
  } else {
    backBtnHtml = `<div style="width: 36px"></div>`; // spacer
  }

  let rightActionHtml = '';
  if (title) {
    rightActionHtml = `<span style="font-size: 13px; font-weight: 600; color: var(--text-secondary); background: var(--bg-secondary); padding: 4px 8px; border-radius: var(--radius-sm);">${title}</span>`;
  } else {
    rightActionHtml = `
      <button class="header-action" id="header-bell-btn" aria-label="Notifications" style="font-size: 18px; position: relative; background: none; border: none; cursor: pointer;">
        🔔
        <span style="position: absolute; top: 6px; right: 6px; width: 7px; height: 7px; background-color: #d63031; border-radius: 50%; border: 1.5px solid var(--bg-primary);"></span>
      </button>
    `;
  }
  
  headerContainer.innerHTML = `
    <header class="app-header">
      ${backBtnHtml}
      <a href="${getPath('index.html')}" class="app-logo" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
        <img src="${getPath('assets/logo.png')}" alt="LASO Logo" class="logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';" style="height: 30px; max-height: 30px; object-fit: contain;">
        <span class="logo-text" style="display: none;">LASO<span>.</span></span>
      </a>
      <div style="min-width: 36px; display: flex; justify-content: flex-end; align-items: center;">
        ${rightActionHtml}
      </div>
    </header>
  `;

  // Attach Bell click listener
  const bellBtn = document.getElementById('header-bell-btn');
  if (bellBtn) {
    const notificationsList = [
      { title: 'New message 💬', msg: 'Amal Perera: "I can come by tomorrow at 10 AM"', icon: '💬' },
      { title: 'Job accepted ⚡', msg: 'Nimal Silva has accepted your repair inquiry.', icon: '⚡' },
      { title: 'Review left ⭐', msg: 'Azaam Customer rated your service 5 stars!', icon: '⭐' },
      { title: 'System Alert 🔔', msg: 'GPS coordinates successfully calibrated.', icon: '🎯' }
    ];
    bellBtn.addEventListener('click', () => {
      const item = notificationsList[Math.floor(Math.random() * notificationsList.length)];
      showNotification(item.title, item.msg, item.icon);
    });
  }
}

// Show Premium Glassmorphic Notification Toast
export function showNotification(title, message, icon = '🔔') {
  const appContainer = document.querySelector('.app-container');
  if (!appContainer) return;

  // Remove existing toast if visible
  let toast = document.getElementById('laso-toast');
  if (toast) {
    toast.remove();
  }

  // Create new toast
  toast = document.createElement('div');
  toast.id = 'laso-toast';
  toast.className = 'toast-notification';
  toast.innerHTML = `
    <div class="toast-icon">${icon}</div>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      <div class="toast-message" title="${message}">${message}</div>
    </div>
  `;

  appContainer.appendChild(toast);

  // Trigger browser paint then show
  setTimeout(() => {
    toast.classList.add('show');
  }, 50);

  // Hide after 3.5 seconds
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// Inline SVGs for Navigation
const svgHome = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nav-svg"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>`;
const svgSearch = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nav-svg"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`;
const svgMessages = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nav-svg"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
const svgProfile = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nav-svg"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

// Initialize Bottom Navigation Bar
export function initBottomNav(activeTab) {
  const navContainer = document.getElementById('nav-container');
  if (!navContainer) return;
  
  const userStr = localStorage.getItem('laso_session_user');
  if (!userStr) return;
  
  let user;
  try {
    user = JSON.parse(userStr);
  } catch (e) {
    return;
  }
  
  let navItems = [];
  if (user.userType === 'customer') {
    navItems = [
      { id: 'home', label: 'Home', icon: svgHome, url: getPath('pages/customer/dashboard.html') },
      { id: 'search', label: 'Search', icon: svgSearch, url: getPath('pages/customer/dashboard.html?focus=search') },
      { id: 'messages', label: 'Messages', icon: svgMessages, url: getPath('pages/customer/messages.html') },
      { id: 'profile', label: 'Profile', icon: svgProfile, url: getPath('pages/shared/profile-view.html') }
    ];
  } else if (user.userType === 'provider') {
    navItems = [
      { id: 'home', label: 'Home', icon: svgHome, url: getPath('pages/provider/dashboard.html') },
      { id: 'messages', label: 'Messages', icon: svgMessages, url: getPath('pages/provider/messages.html') },
      { id: 'profile', label: 'Profile', icon: svgProfile, url: getPath('pages/shared/profile-view.html') }
    ];
  }
  
  let html = `<nav class="bottom-nav">`;
  for (const item of navItems) {
    const isActive = item.id === activeTab ? 'active' : '';
    html += `
      <a href="${item.url}" class="nav-item ${isActive}">
        <span class="nav-icon-container">
          ${item.icon}
        </span>
        <span class="nav-label">${item.label}</span>
      </a>
    `;
  }
  html += `</nav>`;
  
  navContainer.innerHTML = html;
}
