import { checkAuth, DISTRICTS, SERVICES, getQueryParams, getStarsHTML } from './utils.js';
import { initHeader, initBottomNav } from './components.js';
import { fetchProviderDetails, fetchProviderProfile, updateProviderProfile, fetchConversations, fetchMessageThread, sendMessage } from './api.js';

let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
  currentUser = checkAuth('provider');
  if (!currentUser) return;

  const path = window.location.pathname;

  if (path.includes('dashboard.html')) {
    initDashboardPage();
  } else if (path.includes('edit-profile.html')) {
    initEditProfilePage();
  } else if (path.includes('messages.html')) {
    initMessagesPage();
  }
});

// --- PROVIDER DASHBOARD ---
async function initDashboardPage() {
  initHeader('', false);
  initBottomNav('home');

  const profileSummaryCard = document.getElementById('provider-summary-card');
  const reviewsSummaryContainer = document.getElementById('reviews-summary-list');

  try {
    const provider = await fetchProviderDetails(currentUser.userId);
    const category = SERVICES.find(s => s.id === provider.serviceType);
    const categoryEmoji = category ? category.emoji : '🛠️';
    const categoryName = category ? category.name : provider.serviceType;

    // Render stats
    if (profileSummaryCard) {
      profileSummaryCard.innerHTML = `
        <div class="flex items-center gap-8" style="margin-bottom: 16px;">
          <div style="font-size: 40px; background: var(--bg-secondary); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border-color);">
            ${categoryEmoji}
          </div>
          <div>
            <h2 style="font-size: 18px; font-weight: 700; color: var(--text-primary);">${provider.name}</h2>
            <span class="badge badge-info" style="font-size: 11px; margin-top: 4px;">${categoryName} Specialist</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
          <div style="background: var(--bg-secondary); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-size: 11px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase;">Average Rating</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--text-primary); margin: 4px 0 2px 0;">${provider.avgRating.toFixed(1)}</div>
            <div>${'★'.repeat(Math.round(provider.avgRating))}</div>
          </div>
          <div style="background: var(--bg-secondary); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-size: 11px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase;">Total Reviews</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--text-primary); margin: 4px 0 2px 0;">${provider.reviewsCount}</div>
            <div style="font-size: 11px; color: var(--text-secondary);">Customer feedback</div>
          </div>
        </div>

        <div style="border-top: 1px solid var(--border-color); padding-top: 12px; margin-top: 16px; font-size: 13px;">
          <div style="margin-bottom: 6px;"><span style="color: var(--text-secondary);">Coverage:</span> <strong>${provider.district} District</strong></div>
          <div><span style="color: var(--text-secondary);">Address:</span> <strong>${provider.address || 'Not specified'}</strong></div>
        </div>
      `;
    }

    // Render reviews
    if (reviewsSummaryContainer) {
      if (provider.reviews && provider.reviews.length > 0) {
        let reviewsHtml = '';
        provider.reviews.forEach(r => {
          reviewsHtml += `
            <div style="border-bottom: 1px solid var(--border-color); padding: 12px 0;" class="animate-fade-in">
              <div class="flex justify-between items-center" style="margin-bottom: 4px;">
                <strong style="font-size: 13px; color: var(--text-primary);">${r.customerName}</strong>
                <span style="font-size: 11px; color: var(--text-secondary);">${r.date}</span>
              </div>
              <div style="color: #ffb703; font-size: 12px; margin-bottom: 4px;">
                ${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}
              </div>
              <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4; font-style: italic;">"${r.comment}"</p>
            </div>
          `;
        });
        reviewsSummaryContainer.innerHTML = reviewsHtml;
      } else {
        reviewsSummaryContainer.innerHTML = `
          <div style="text-align: center; padding: 24px 0; color: var(--text-secondary); font-size: 13px;">
            No customer reviews logged yet.
          </div>
        `;
      }
    }

  } catch (err) {
    console.error(err);
  }

  // Show a mock inquiry notification after 4 seconds
  setTimeout(() => {
    import('./components.js').then(m => {
      m.showNotification('New Inquiry ⚡', 'Azaam Customer: "Hi, is tomorrow morning free for inspection?"', '⚡');
    });
  }, 4000);
}

// --- EDIT PROFILE ---
async function initEditProfilePage() {
  initHeader('Edit Profile', true);
  initBottomNav('profile');

  const form = document.getElementById('edit-profile-form');
  const phoneInput = document.getElementById('phone');
  const districtSelect = document.getElementById('district');
  const addressInput = document.getElementById('address');
  const latInput = document.getElementById('lat');
  const lonInput = document.getElementById('lon');
  const descTextarea = document.getElementById('description');
  const gpsBtn = document.getElementById('btn-gps');
  const errorAlert = document.getElementById('error-alert');
  const submitBtn = form.querySelector('button[type="submit"]');

  try {
    const provider = await fetchProviderProfile(currentUser.userId);

    // Pre-populate fields
    if (phoneInput) phoneInput.value = provider.phone || '';
    if (districtSelect) districtSelect.value = provider.district || '';
    if (addressInput) addressInput.value = provider.address || '';
    if (latInput) latInput.value = provider.lat || '';
    if (lonInput) lonInput.value = provider.lon || '';
    if (descTextarea) descTextarea.value = provider.description || '';

    // Coordinates listener fallback
    if (districtSelect) {
      districtSelect.addEventListener('change', () => {
        const district = districtSelect.value;
        if (district && DISTRICTS[district]) {
          latInput.value = DISTRICTS[district].lat;
          lonInput.value = DISTRICTS[district].lon;
        }
      });
    }

    // Geolocation handler
    if (gpsBtn) {
      gpsBtn.addEventListener('click', () => {
        gpsBtn.disabled = true;
        gpsBtn.textContent = '⌛ Fetching...';

        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (pos) => {
              latInput.value = pos.coords.latitude.toFixed(6);
              lonInput.value = pos.coords.longitude.toFixed(6);
              gpsBtn.disabled = false;
              gpsBtn.textContent = 'Captured';
              setTimeout(() => { gpsBtn.textContent = '🎯 Update GPS'; }, 2000);
            },
            () => {
              alert('Could not captured location. Reverting to district fallback coordinates.');
              gpsBtn.disabled = false;
              gpsBtn.textContent = '❌ Retry';
            }
          );
        } else {
          gpsBtn.textContent = '❌ Unsupported';
        }
      });
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorAlert.style.display = 'none';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving Changes...';

      const updateData = {
        phone: phoneInput.value.trim(),
        district: districtSelect.value,
        address: addressInput.value.trim(),
        lat: parseFloat(latInput.value),
        lon: parseFloat(lonInput.value),
        description: descTextarea.value.trim()
      };

      try {
        await updateProviderProfile(currentUser.userId, updateData);
        alert('Profile details updated successfully!');
        window.location.href = '../shared/profile-view.html';
      } catch (err) {
        errorAlert.textContent = err.message || 'Failed to update profile details.';
        errorAlert.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Changes';
      }
    });

  } catch (err) {
    alert('Failed to load profile details.');
  }
}

// --- PROVIDER MESSAGES / CHAT ---
let chatInterval = null;

function initMessagesPage() {
  const params = getQueryParams();
  const contactId = params.contactId;
  const nav = document.getElementById('nav-container');

  if (contactId) {
    initHeader('Chat', true);
    if (nav) nav.style.display = 'none';
    initChatThreadView(contactId);
  } else {
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
      <p style="color: var(--text-secondary); margin-top: 8px;">Loading inbox...</p>
    </div>
  `;

  try {
    const conversations = await fetchConversations(currentUser.userId);

    if (conversations.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 60px 16px;">
          <span style="font-size: 48px;">💬</span>
          <h3 style="font-size: 16px; font-weight: 700; margin-top: 16px; color: var(--text-primary);">No Messages</h3>
          <p style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Incoming service inquiries from customers will appear here.</p>
        </div>
      `;
      return;
    }

    let html = '<div class="animate-fade-in">';
    conversations.forEach(c => {
      const timeString = new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      html += `
        <div class="card flex items-center" style="gap: 12px; cursor: pointer; padding: 14px;" onclick="window.location.href='messages.html?contactId=${c.partnerId}'">
          <div style="font-size: 24px; background: var(--bg-secondary); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            👤
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
    container.innerHTML = `<div class="card text-center" style="padding: 24px;"><p style="color:#d63031;">Failed to load messages inbox</p></div>`;
  }
}

async function initChatThreadView(partnerId) {
  const container = document.getElementById('messages-container');

  container.classList.add('flex', 'flex-col');
  container.style.height = 'calc(100% - 60px)';
  container.style.paddingBottom = '70px';

  let customerName = 'Customer';
  try {
    const users = JSON.parse(localStorage.getItem('laso_mock_users')) || [];
    const u = users.find(usr => usr.id === partnerId);
    if (u) customerName = u.name;
  } catch (e) {}

  container.innerHTML = `
    <div style="background: var(--bg-primary); border-bottom: 1px solid var(--border-color); padding: 8px 16px; margin: -20px -16px 12px -16px;" class="flex items-center gap-8">
      <div style="font-size: 24px; width: 36px; height: 36px; border-radius: 50%; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center;">
        👤
      </div>
      <div>
        <h4 style="font-size: 14px; font-weight: 700; margin: 0;">${customerName}</h4>
        <span style="font-size: 11px; color: var(--text-secondary);">Client inquiry</span>
      </div>
    </div>

    <div id="chat-thread-container" style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-bottom: 12px;">
      <!-- Message bubbles -->
    </div>

    <form id="chat-send-form" class="chat-input-bar">
      <input type="text" id="chat-input-field" class="form-control" placeholder="Type a response..." required autocomplete="off" style="border-radius: var(--radius-lg);">
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
        html = `<div style="text-align: center; color: var(--text-secondary); font-size: 12px; margin-top: 40px;">No message log. Send a greeting to start.</div>`;
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

      if (isScrollAtBottom || threadContainer.dataset.loaded !== 'true') {
        threadContainer.scrollTop = threadContainer.scrollHeight;
        threadContainer.dataset.loaded = 'true';
      }
    } catch (e) {}
  }

  loadThread();
  chatInterval = setInterval(loadThread, 3000);

  window.addEventListener('beforeunload', () => {
    clearInterval(chatInterval);
  });

  sendForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = inputField.value.trim();
    if (!text) return;

    inputField.value = '';

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
      tempBubble.remove();
      alert('Failed to send message.');
    }
  });
}
