export const DISTRICTS = {
  "Colombo": { lat: 6.9271, lon: 79.8612 },
  "Gampaha": { lat: 7.0873, lon: 80.0144 },
  "Kalutara": { lat: 6.5854, lon: 79.9607 },
  "Kandy": { lat: 7.2906, lon: 80.6337 },
  "Matale": { lat: 7.4675, lon: 80.6234 },
  "Nuwara Eliya": { lat: 6.9497, lon: 80.7891 },
  "Galle": { lat: 6.0535, lon: 80.2210 },
  "Matara": { lat: 5.9549, lon: 80.5550 },
  "Hambantota": { lat: 6.1248, lon: 81.1185 },
  "Jaffna": { lat: 9.6615, lon: 80.0255 },
  "Kilinochchi": { lat: 9.3803, lon: 80.3983 },
  "Mannar": { lat: 8.9810, lon: 79.9044 },
  "Vavuniya": { lat: 8.7542, lon: 80.4982 },
  "Mullaitivu": { lat: 9.2671, lon: 80.8143 },
  "Batticaloa": { lat: 7.7310, lon: 81.6747 },
  "Ampara": { lat: 7.3018, lon: 81.6747 },
  "Trincomalee": { lat: 8.5873, lon: 81.2152 },
  "Kurunegala": { lat: 7.4863, lon: 80.3647 },
  "Puttalam": { lat: 8.0362, lon: 79.8283 },
  "Anuradhapura": { lat: 8.3114, lon: 80.4037 },
  "Polonnaruwa": { lat: 7.9403, lon: 81.0188 },
  "Badulla": { lat: 6.9934, lon: 81.0550 },
  "Moneragala": { lat: 6.8724, lon: 81.3507 },
  "Ratnapura": { lat: 6.7056, lon: 80.3847 },
  "Kegalle": { lat: 7.2513, lon: 80.3464 }
};

// Service Categories
export const SERVICES = [
  { id: 'plumbing', name: 'Plumbing', emoji: '🧰', description: 'pipe repair, tap installation, water tank issues, drain unblocking' },
  { id: 'electrical', name: 'Electrical', emoji: '⚡', description: 'wiring, fixture installation, circuit breaker repair, fan/light repair' },
  { id: 'carpentry', name: 'Carpentry', emoji: '🔨', description: 'furniture making, door/window repair, wood polishing' },
  { id: 'masonry', name: 'Masonry', emoji: '🧱', description: 'brick/block work, plastering, tiling, concrete work' },
  { id: 'painting', name: 'Painting', emoji: '🎨', description: 'interior/exterior painting, wallpapering' },
  { id: 'appliance', name: 'Appliance Repair', emoji: '📺', description: 'refrigerator, washing machine, AC, microwave repair' },
  { id: 'ac', name: 'AC Repair & Maintenance', emoji: '❄️', description: 'cleaning, gas refilling, installation' },
  { id: 'cleaning', name: 'Cleaning Services', emoji: '🧹', description: 'home/office cleaning, carpet cleaning, post-construction clean-up' }
];

// Haversine Distance Formula in Kilometers
export function calculateDistance(lat1, lon1, lat2, lon2) {
  if (lat1 === undefined || lon1 === undefined || lat2 === undefined || lon2 === undefined) return 0;
  const R = 6371; // Earth Radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return parseFloat((R * c).toFixed(1));
}

// Parse URL Query parameters
export function getQueryParams() {
  const params = {};
  const search = window.location.search.substring(1);
  if (!search) return params;
  const pairs = search.split('&');
  for (const pair of pairs) {
    const [key, value] = pair.split('=');
    params[decodeURIComponent(key)] = decodeURIComponent(value || '');
  }
  return params;
}

// Generate stars HTML for rating
export function getStarsHTML(rating) {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;
  
  let html = '<span class="rating-stars">';
  html += '★'.repeat(fullStars);
  if (halfStar) html += '½'; // or just use full star if half star emoji is not supported
  html += '☆'.repeat(emptyStars);
  html += ` <span style="color: var(--text-secondary); font-size: 13px; font-weight: 500;">(${rating.toFixed(1)})</span>`;
  html += '</span>';
  return html;
}

// Get user session data
export function getSessionUser() {
  const userStr = localStorage.getItem('laso_session_user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
}

// Set user session data
export function setSessionUser(user) {
  localStorage.setItem('laso_session_user', JSON.stringify(user));
}

// Clear user session
export function clearSession() {
  localStorage.removeItem('laso_session_user');
}

// Check auth and redirect
export function checkAuth(requiredType = null) {
  const user = getSessionUser();
  const path = window.location.pathname;
  
  if (!user) {
    // Determine path back to login
    if (!path.includes('/auth/')) {
      const depth = (path.match(/\//g) || []).length;
      let prefix = '';
      if (depth === 2) prefix = './pages/auth/';
      else if (depth === 3) prefix = '../auth/';
      else if (depth === 4) prefix = '../../auth/';
      window.location.href = prefix ? `${prefix}login.html` : '/pages/auth/login.html';
    }
    return null;
  }
  
  if (requiredType && user.userType !== requiredType) {
    // Redirect to correct dashboard
    const prefix = path.includes('/pages/') ? '../' : './pages/';
    window.location.href = `${prefix}${user.userType}/dashboard.html`;
  }
  
  return user;
}
