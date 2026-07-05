import { checkAuth, DISTRICTS, SERVICES, getQueryParams, getStarsHTML, calculateDistance } from './utils.js';
import { initHeader, initBottomNav } from './components.js';
import { fetchNearbyProviders, fetchProviderDetails, submitReview, fetchConversations, fetchMessageThread, sendMessage } from './api.js';

let currentUser = null;
let currentCoords = null;

document.addEventListener('DOMContentLoaded', () => {
  currentUser = checkAuth('customer');
  if (!currentUser) return;

  const path = window.location.pathname;

  if (path.includes('dashboard.html')) {
    initDashboardPage();
  } else if (path.includes('provider-detail.html')) {
    initProviderDetailPage();
  } else if (path.includes('rate-review.html')) {
    initRateReviewPage();
  } else if (path.includes('messages.html')) {
    initMessagesPage();
  }
});

// --- CUSTOMER DASHBOARD ---
async function initDashboardPage() {
  const params = getQueryParams();
  const focusSearch = params.focus === 'search';

  initHeader('', false);
  initBottomNav(focusSearch ? 'search' : 'home');

  const searchInput = document.getElementById('search-input');
  const districtSelect = document.getElementById('district-filter');
  const categoryChipsContainer = document.getElementById('category-chips');
  const providerListContainer = document.getElementById('provider-list');

  if (focusSearch && searchInput) {
    searchInput.focus();
  }

  // Set default district to customer's registered district
  if (districtSelect && currentUser.district) {
    districtSelect.value = currentUser.district;
  }

  // Populate category chips
  if (categoryChipsContainer) {
    let chipsHtml = `<button class="chip active" data-category="">All Services</button>`;
    SERVICES.forEach(s => {
      chipsHtml += `<button class="chip" data-category="${s.id}">${s.emoji} ${s.name}</button>`;
    });
    categoryChipsContainer.innerHTML = chipsHtml;

    // Chips click listeners
    const chips = categoryChipsContainer.querySelectorAll('.chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        refreshProviders();
      });
    });
  }

  // District filter change listener
  if (districtSelect) {
    districtSelect.addEventListener('change', () => {
      refreshProviders();
    });
  }

  // Search input listener with simple debounce
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(refreshProviders, 300);
    });
  }

  // Fetch coordinates (GPS first, fallback to selected district center)
  async function resolveCoordinates(selectedDistrict) {
    return new Promise((resolve) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude });
          },
          () => {
            // Fallback to district coordinates
            const coords = DISTRICTS[selectedDistrict] || DISTRICTS['Colombo'];
            resolve(coords);
          },
          { timeout: 3000 }
        );
      } else {
        const coords = DISTRICTS[selectedDistrict] || DISTRICTS['Colombo'];
        resolve(coords);
      }
    });
  }

  async function refreshProviders() {
    providerListContainer.innerHTML = `
      <div style="text-align: center; padding: 40px 0;">
        <span style="font-size: 24px;">⌛</span>
        <p style="color: var(--text-secondary); margin-top: 8px;">Finding nearby providers...</p>
      </div>
    `;

    const selectedDistrict = districtSelect ? districtSelect.value : currentUser.district;
    const activeChip = categoryChipsContainer.querySelector('.chip.active');
    const selectedCategory = activeChip ? activeChip.getAttribute('data-category') : '';
    const searchVal = searchInput ? searchInput.value.trim() : '';

    if (!currentCoords || (districtSelect && districtSelect.dataset.lastDistrict !== selectedDistrict)) {
      currentCoords = await resolveCoordinates(selectedDistrict);
      if (districtSelect) districtSelect.dataset.lastDistrict = selectedDistrict;
    }

    try {
      const providers = await fetchNearbyProviders(
        currentCoords.lat,
        currentCoords.lon,
        selectedDistrict,
        selectedCategory,
        searchVal
      );

      renderProvidersList(providers);
    } catch (err) {
      providerListContainer.innerHTML = `
        <div class="card text-center" style="padding: 24px;">
          <p style="color: #d63031; font-weight: 500;">Failed to load providers</p>
          <button id="retry-btn" class="btn btn-secondary text-sm" style="margin-top: 12px; width: auto; display: inline-flex;">Retry</button>
        </div>
      `;
      document.getElementById('retry-btn')?.addEventListener('click', refreshProviders);
    }
  }

  function renderProvidersList(providers) {
    if (providers.length === 0) {
      providerListContainer.innerHTML = `
        <div style="text-align: center; padding: 40px 16px;">
          <span style="font-size: 40px;">🔍</span>
          <h3 style="font-size: 16px; font-weight: 700; margin-top: 12px; color: var(--text-primary);">No Providers Found</h3>
          <p style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Try expanding your district or searching other categories.</p>
        </div>
      `;
      return;
    }

    let html = '';
    providers.forEach(p => {
      const category = SERVICES.find(s => s.id === p.serviceType);
      const categoryEmoji = category ? category.emoji : '🛠️';
      const categoryName = category ? category.name : p.serviceType;
      
      // District details
      const distanceText = p.distance !== undefined ? `${p.distance} km away in ` : '';

      html += `
        <div class="card animate-fade-in" style="cursor: pointer;" onclick="window.location.href='provider-detail.html?id=${p.id}'">
          <div class="flex justify-between items-center" style="margin-bottom: 8px;">
            <span class="badge badge-info" style="font-size: 11px;">${categoryEmoji} ${categoryName}</span>
            <span style="font-size: 12px; font-weight: 600; color: var(--primary-color);">${distanceText}${p.district}</span>
          </div>
          <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 4px; color: var(--text-primary);">${p.name}</h3>
          <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            ${p.description || 'No description provided.'}
          </p>
          <div style="border-top: 1px solid var(--border-color); padding-top: 10px;" class="flex justify-between items-center">
            ${getStarsHTML(p.avgRating || 5)}
            <span style="font-size: 12px; color: var(--text-secondary);">${p.reviewsCount || 0} reviews</span>
          </div>
        </div>
      `;
    });

    providerListContainer.innerHTML = html;
  }

  // Initial load
  refreshProviders();

  // Show a mock welcome notification after 4 seconds
  setTimeout(() => {
    import('./components.js').then(m => {
      m.showNotification('Message Received 💬', 'Amal Perera: "Hi! I can come by tomorrow at 10 AM."', '💬');
    });
  }, 4000);
}

// --- PROVIDER DETAILS ---
async function initProviderDetailPage() {
  const params = getQueryParams();
  const providerId = params.id;

  if (!providerId) {
    window.location.href = 'dashboard.html';
    return;
  }

  initHeader('Details', true);
  initBottomNav('home');

  const detailContainer = document.getElementById('provider-details-container');

  try {
    const provider = await fetchProviderDetails(providerId);
    const category = SERVICES.find(s => s.id === provider.serviceType);
    const categoryEmoji = category ? category.emoji : '🛠️';
    const categoryName = category ? category.name : provider.serviceType;

    let reviewsHtml = '';
    if (provider.reviews && provider.reviews.length > 0) {
      provider.reviews.forEach(r => {
        reviewsHtml += `
          <div style="border-bottom: 1px solid var(--border-color); padding: 12px 0;">
            <div class="flex justify-between items-center" style="margin-bottom: 4px;">
              <strong style="font-size: 14px; color: var(--text-primary);">${r.customerName}</strong>
              <span style="font-size: 11px; color: var(--text-secondary);">${r.date}</span>
            </div>
            <div style="margin-bottom: 6px;">
              ${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">${r.comment}</p>
          </div>
        `;
      });
    } else {
      reviewsHtml = `<p style="text-align: center; color: var(--text-secondary); font-size: 13px; padding: 20px 0;">No reviews yet. Be the first to review!</p>`;
    }

    detailContainer.innerHTML = `
      <div class="animate-fade-in">
        <!-- Provider Info Header -->
        <div class="card" style="text-align: center; padding: 24px 16px;">
          <div style="font-size: 48px; margin-bottom: 8px;">${categoryEmoji}</div>
          <h2 style="font-size: 20px; font-weight: 700; color: var(--text-primary);">${provider.name}</h2>
          <span class="badge badge-info" style="margin-top: 6px; font-size: 12px;">${categoryName} Specialist</span>
          
          <div style="margin-top: 12px; display: flex; justify-content: center;">
            ${getStarsHTML(provider.avgRating || 5)}
          </div>
        </div>

        <!-- Details Card -->
        <div class="card">
          <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">Contact & Location</h3>
          <div style="font-size: 13px; display: flex; flex-direction: column; gap: 8px;">
            <div><span style="color: var(--text-secondary);">Phone:</span> <strong style="color: var(--text-primary);">${provider.phone}</strong></div>
            <div><span style="color: var(--text-secondary);">District:</span> <strong style="color: var(--text-primary);">${provider.district}</strong></div>
            <div><span style="color: var(--text-secondary);">Address:</span> <strong style="color: var(--text-primary);">${provider.address || 'N/A'}</strong></div>
            <div><span style="color: var(--text-secondary);">Coordinates:</span> <code style="background: var(--bg-secondary); padding: 2px 4px; border-radius: 4px; font-size: 11px;">${provider.lat.toFixed(4)}, ${provider.lon.toFixed(4)}</code></div>
          </div>
        </div>

        <!-- Description Card -->
        <div class="card">
          <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 8px;">About Service</h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${provider.description || 'No service description provided.'}</p>
        </div>

        <!-- Actions -->
        <div class="flex" style="gap: 12px; margin-bottom: 24px;">
          <button id="btn-message" class="btn btn-primary" style="flex: 1;"><span style="font-size: 16px;">💬</span> Message</button>
          <button id="btn-review-redirect" class="btn btn-secondary" style="flex: 1;"><span style="font-size: 16px;">★</span> Review</button>
        </div>

        <!-- Reviews Card -->
        <div class="card" style="margin-bottom: 24px;">
          <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px;">Reviews (${provider.reviewsCount})</h3>
          <div>${reviewsHtml}</div>
        </div>
      </div>
    `;

    document.getElementById('btn-message').addEventListener('click', () => {
      window.location.href = `messages.html?contactId=${provider.id}`;
    });

    document.getElementById('btn-review-redirect').addEventListener('click', () => {
      window.location.href = `rate-review.html?id=${provider.id}`;
    });

  } catch (err) {
    detailContainer.innerHTML = `<div class="card text-center" style="padding: 24px;"><p style="color:#d63031;">${err.message}</p></div>`;
  }
}

// --- RATE & REVIEW ---
function initRateReviewPage() {
  const params = getQueryParams();
  const providerId = params.id;

  if (!providerId) {
    window.location.href = 'dashboard.html';
    return;
  }

  initHeader('Write Review', true);
  initBottomNav('home');

  const ratingForm = document.getElementById('review-form');
  const starInputs = document.querySelectorAll('.star-rating input');
  const errorAlert = document.getElementById('error-alert');

  // Load provider name
  fetchProviderDetails(providerId).then(p => {
    document.getElementById('provider-name-review').textContent = p.name;
  });

  if (ratingForm) {
    ratingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorAlert.style.display = 'none';

      const selectedRating = ratingForm.querySelector('input[name="rating"]:checked');
      const comment = document.getElementById('comment').value.trim();

      if (!selectedRating) {
        errorAlert.textContent = 'Please select a rating (1 to 5 stars)';
        errorAlert.style.display = 'block';
        return;
      }

      const ratingValue = selectedRating.value;

      try {
        await submitReview(providerId, ratingValue, comment);
        alert('Review submitted successfully!');
        window.location.href = `provider-detail.html?id=${providerId}`;
      } catch (err) {
        errorAlert.textContent = err.message || 'Failed to submit review. Try again.';
        errorAlert.style.display = 'block';
      }
    });
  }
}

// --- MESSAGES / CHAT ---
let chatInterval = null;

function initMessagesPage() {
  const params = getQueryParams();
  const contactId = params.contactId;
  const nav = document.getElementById('nav-container');

  if (contactId) {
    // Open direct message window
    initHeader('Chat', true);
    if (nav) nav.style.display = 'none';
    initChatThreadView(contactId);
  } else {
    // Open inbox conversation list
    initHeader('Inbox', false);
    if (nav) nav.style.display = 'block';
    initBottomNav('messages');
    initConversationListView();
  }
}

async function initConversationListView() {
  const container = document.getElementById('messages-container');
  container.innerHTML = `
    <div style="text-align: center; padding: 40px 0;">
      <span style="font-size: 24px;">⌛</span>
      <p style="color: var(--text-secondary); margin-top: 8px;">Loading conversations...</p>
    </div>
  `;

  try {
    const conversations = await fetchConversations(currentUser.userId);
    
    if (conversations.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 60px 16px;">
          <span style="font-size: 48px;">💬</span>
          <h3 style="font-size: 16px; font-weight: 700; margin-top: 16px; color: var(--text-primary);">No Messages Yet</h3>
          <p style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Locate providers on the dashboard and contact them to start a conversation.</p>
        </div>
      `;
      return;
    }

    let html = '<div class="animate-fade-in">';
    conversations.forEach(c => {
      const partnerCategory = SERVICES.find(s => s.id === c.partnerService);
      const partnerEmoji = partnerCategory ? partnerCategory.emoji : '👤';
      const timeString = new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      html += `
        <div class="card flex items-center" style="gap: 12px; cursor: pointer; padding: 14px;" onclick="window.location.href='messages.html?contactId=${c.partnerId}'">
          <div style="font-size: 32px; background: var(--bg-secondary); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            ${partnerEmoji}
          </div>
          <div style="flex: 1; min-width: 0;">
            <div class="flex justify-between items-center" style="margin-bottom: 2px;">
              <strong style="font-size: 14px; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${c.partnerName}</strong>
              <span style="font-size: 11px; color: var(--text-secondary);">${timeString}</span>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; margin: 0;">
              ${c.lastMessage}
            </p>
          </div>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;

  } catch (err) {
    container.innerHTML = `<div class="card text-center" style="padding: 24px;"><p style="color:#d63031;">Failed to load conversations</p></div>`;
  }
}

async function initChatThreadView(partnerId) {
  const container = document.getElementById('messages-container');
  
  // Set layout for direct messaging (appends chat bar, shrinks scrollable view)
  container.classList.add('flex', 'flex-col');
  container.style.height = 'calc(100% - 60px)'; // subtract header
  container.style.paddingBottom = '70px'; // space for input bar

  let partnerName = 'Provider';
  let partnerEmoji = '🛠️';
  try {
    const details = await fetchProviderDetails(partnerId);
    partnerName = details.name;
    const cat = SERVICES.find(s => s.id === details.serviceType);
    partnerEmoji = cat ? cat.emoji : '🛠️';
  } catch (e) {}

  // Inject structural HTML for chat thread
  container.innerHTML = `
    <div style="background: var(--bg-primary); border-bottom: 1px solid var(--border-color); padding: 8px 16px; margin: -20px -16px 12px -16px;" class="flex items-center gap-8">
      <div style="font-size: 24px; width: 36px; height: 36px; border-radius: 50%; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center;">
        ${partnerEmoji}
      </div>
      <div>
        <h4 style="font-size: 14px; font-weight: 700; margin: 0;">${partnerName}</h4>
        <span style="font-size: 11px; color: var(--text-secondary);">Online</span>
      </div>
    </div>
    
    <div id="chat-thread-container" style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-bottom: 12px;">
      <!-- Message bubbles go here -->
    </div>

    <form id="chat-send-form" class="chat-input-bar">
      <input type="text" id="chat-input-field" class="form-control" placeholder="Type a message..." required autocomplete="off" style="border-radius: var(--radius-lg);">
      <button type="submit" class="btn btn-primary" style="width: auto; padding: 12px 18px; border-radius: 50%; font-size: 16px; height: 45px; align-self: center;">
        ✈️
      </button>
    </form>
  `;

  const threadContainer = document.getElementById('chat-thread-container');
  const sendForm = document.getElementById('chat-send-form');
  const inputField = document.getElementById('chat-input-field');

  async function loadThread() {
    try {
      const messages = await fetchMessageThread(currentUser.userId, partnerId);
      
      let html = '';
      if (messages.length === 0) {
        html = `
          <div style="text-align: center; color: var(--text-secondary); font-size: 12px; margin-top: 40px; padding: 0 20px;">
            Connection established. Send a message to start negotiating details.
          </div>
        `;
      } else {
        messages.forEach(m => {
          const isSent = m.senderId === currentUser.userId;
          html += `
            <div class="message-bubble ${isSent ? 'message-sent' : 'message-received'}">
              <div>${m.text}</div>
              <div style="font-size: 9px; text-align: right; margin-top: 4px; opacity: 0.8;">
                ${new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          `;
        });
      }
      
      const isScrollAtBottom = threadContainer.scrollHeight - threadContainer.scrollTop <= threadContainer.clientHeight + 100;
      threadContainer.innerHTML = html;

      // Force scroll to bottom on initial load, or if user is already at the bottom
      if (isScrollAtBottom || threadContainer.dataset.loaded !== 'true') {
        threadContainer.scrollTop = threadContainer.scrollHeight;
        threadContainer.dataset.loaded = 'true';
      }
    } catch (e) {}
  }

  // Load message thread initially and periodically
  loadThread();
  chatInterval = setInterval(loadThread, 3000);

  // Clean up interval on page change
  window.addEventListener('beforeunload', () => {
    clearInterval(chatInterval);
  });

  // Handle Send Button click
  sendForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = inputField.value.trim();
    if (!text) return;

    inputField.value = '';
    
    // Optimistic UI updates
    const tempBubble = document.createElement('div');
    tempBubble.className = 'message-bubble message-sent';
    tempBubble.innerHTML = `
      <div>${text}</div>
      <div style="font-size: 9px; text-align: right; margin-top: 4px; opacity: 0.8;">⌛ Sending...</div>
    `;
    threadContainer.appendChild(tempBubble);
    threadContainer.scrollTop = threadContainer.scrollHeight;

    try {
      await sendMessage(currentUser.userId, partnerId, text);
      loadThread();
    } catch (err) {
      alert('Message failed to send.');
      tempBubble.remove();
    }
  });
}


