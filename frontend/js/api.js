import { DISTRICTS, calculateDistance } from './utils.js';

// Configuration
export const API_BASE_URL = 'http://localhost:8000'; // Default Python backend port
export const USE_MOCK_API = true; // Toggle to false to enforce real API requests

// --- Mock Database Initializer ---
const MOCK_PROVIDERS_KEY = 'laso_mock_providers';
const MOCK_USERS_KEY = 'laso_mock_users';
const MOCK_REVIEWS_KEY = 'laso_mock_reviews';
const MOCK_MESSAGES_KEY = 'laso_mock_messages';

function initMockDatabase() {
  if (!localStorage.getItem(MOCK_PROVIDERS_KEY)) {
    const defaultProviders = [
      {
        id: 'p1',
        name: 'Amal Perera',
        email: 'amal@laso.lk',
        phone: '0771234567',
        userType: 'provider',
        serviceType: 'plumbing',
        district: 'Colombo',
        address: '123 Galle Road, Colombo 03',
        lat: 6.9271,
        lon: 79.8612,
        description: '24/7 plumbing emergency service. Specializing in tap installations, leak repairs, and water pump troubleshooting.',
        avgRating: 4.8,
        reviewsCount: 3
      },
      {
        id: 'p2',
        name: 'Nimal Silva',
        email: 'nimal@laso.lk',
        phone: '0719876543',
        userType: 'provider',
        serviceType: 'electrical',
        district: 'Colombo',
        address: '45 Duplication Road, Colombo 04',
        lat: 6.9312,
        lon: 79.8521,
        description: 'Licensed electrician with 10 years of experience. Services include house wiring, light fixture setup, and safety inspections.',
        avgRating: 4.5,
        reviewsCount: 2
      },
      {
        id: 'p3',
        name: 'Kamal Gunaratne',
        email: 'kamal@laso.lk',
        phone: '0723456789',
        userType: 'provider',
        serviceType: 'carpentry',
        district: 'Gampaha',
        address: '78 Kandy Road, Gampaha',
        lat: 7.0873,
        lon: 80.0144,
        description: 'Quality wood furniture crafting, door installations, polishing, and custom wooden cabinetry repairs.',
        avgRating: 4.9,
        reviewsCount: 4
      },
      {
        id: 'p4',
        name: 'Ruwan Fernando',
        email: 'ruwan@laso.lk',
        phone: '0754567890',
        userType: 'provider',
        serviceType: 'ac',
        district: 'Kandy',
        address: '12 Peradeniya Road, Kandy',
        lat: 7.2906,
        lon: 80.6337,
        description: 'Air conditioner installations, deep chemical washes, gas refilling, and cooling efficiency optimization.',
        avgRating: 4.2,
        reviewsCount: 1
      },













      
      {
        id: 'p5',
        name: 'Sunila Jayasinghe',
        email: 'sunila@laso.lk',
        phone: '0761234789',
        userType: 'provider',
        serviceType: 'cleaning',
        district: 'Galle',
        address: '56 Matara Road, Galle',
        lat: 6.0535,
        lon: 80.2210,
        description: 'Reliable office and home cleaning. Move-in/move-out deep cleaning, post-construction cleanup, and carpet washing.',
        avgRating: 4.7,
        reviewsCount: 2
      }
    ];
    localStorage.setItem(MOCK_PROVIDERS_KEY, JSON.stringify(defaultProviders));
  }

  if (!localStorage.getItem(MOCK_USERS_KEY)) {
    const defaultUsers = [
      { id: 'c1', name: 'Azaam Customer', email: 'azaam@laso.lk', phone: '0771112223', password: 'password', district: 'Colombo', address: 'Bambalapitiya, Colombo', userType: 'customer' },
      { id: 'p1', name: 'Amal Perera', email: 'amal@laso.lk', phone: '0771234567', password: 'password', district: 'Colombo', address: '123 Galle Road, Colombo 03', serviceType: 'plumbing', lat: 6.9271, lon: 79.8612, description: '24/7 plumbing emergency service...', userType: 'provider' }
    ];
    localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(defaultUsers));
  }

  if (!localStorage.getItem(MOCK_REVIEWS_KEY)) {
    const defaultReviews = [
      { id: 'r1', providerId: 'p1', customerName: 'Harsha Bandara', rating: 5, comment: 'Amal was extremely quick to arrive and fixed my kitchen sink pipe leak in 15 minutes! Very friendly and professional.', date: '2026-05-15' },
      { id: 'r2', providerId: 'p1', customerName: 'Fathima Riza', rating: 4, comment: 'Good quality service, but arrived 10 minutes late. Highly recommend.', date: '2026-05-20' },
      { id: 'r3', providerId: 'p2', customerName: 'Dilshan Silva', rating: 5, comment: 'Nimal rewired our entire living room safely. Fair pricing.', date: '2026-05-22' },
      { id: 'r4', providerId: 'p3', customerName: 'Suresh Kumar', rating: 5, comment: 'Excellent woodwork on our new door frame. Beautiful craftsmanship!', date: '2026-05-24' }
    ];
    localStorage.setItem(MOCK_REVIEWS_KEY, JSON.stringify(defaultReviews));
  }

  if (!localStorage.getItem(MOCK_MESSAGES_KEY)) {
    const defaultMessages = [
      { id: 'm1', senderId: 'c1', receiverId: 'p1', text: 'Hello Amal, do you have time tomorrow morning to inspect a water tank leak?', timestamp: new Date(Date.now() - 3600000 * 2).toISOString() },
      { id: 'm2', senderId: 'p1', receiverId: 'c1', text: 'Hi! Yes, I can come by Colombo around 10:00 AM. Please share your phone number.', timestamp: new Date(Date.now() - 3600000).toISOString() }
    ];
    localStorage.setItem(MOCK_MESSAGES_KEY, JSON.stringify(defaultMessages));
  }
}

// Run initializer
initMockDatabase();

// Help mock API feel asynchronous
function delay(ms = 300) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// --- Dynamic API Client ---

export async function request(endpoint, options = {}) {
  if (USE_MOCK_API) {
    throw new Error('Using Mock API Fallback'); // Automatically trigger the catch block below
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ message: 'Server error occurred' }));
    throw new Error(err.message || 'API request failed');
  }
  return response.json();
}

// API Functions with Mock Fallbacks
export async function loginUser(email, password) {
  try {
    return await request('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  } catch (error) {
    await delay();
    const users = JSON.parse(localStorage.getItem(MOCK_USERS_KEY));
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
    if (!user) {
      throw new Error('Invalid email or password');
    }
    return {
      userId: user.id,
      userType: user.userType,
      name: user.name,
      email: user.email,
      phone: user.phone || '',
      district: user.district,
      address: user.address || ''
    };
  }
}

export async function registerUser(userData) {
  try {
    return await request('/api/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  } catch (error) {
    await delay();
    const users = JSON.parse(localStorage.getItem(MOCK_USERS_KEY));
    if (users.some(u => u.email.toLowerCase() === userData.email.toLowerCase())) {
      throw new Error('An account with this email already exists');
    }

    const newId = (userData.userType === 'customer' ? 'c' : 'p') + (users.length + 1);
    const newUser = { id: newId, ...userData };
    users.push(newUser);
    localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users));

    if (userData.userType === 'provider') {
      const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
      providers.push({
        id: newId,
        name: userData.name,
        email: userData.email,
        phone: userData.phone,
        userType: 'provider',
        serviceType: userData.serviceType,
        district: userData.district,
        address: userData.address,
        lat: parseFloat(userData.lat),
        lon: parseFloat(userData.lon),
        description: userData.description || '',
        avgRating: 5.0,
        reviewsCount: 0
      });
      localStorage.setItem(MOCK_PROVIDERS_KEY, JSON.stringify(providers));
    }

    return {
      userId: newId,
      userType: userData.userType,
      name: userData.name,
      email: userData.email,
      phone: userData.phone || '',
      district: userData.district,
      address: userData.address || ''
    };
  }
}

export async function fetchNearbyProviders(lat, lon, district, serviceCategory = '', searchKeyword = '') {
  try {
    // Member 3 Endpoint: /api/providers/nearby?lat=X&lon=Y&district=Colombo&radius=10
    let query = `/api/providers/nearby?lat=${lat}&lon=${lon}&district=${encodeURIComponent(district)}`;
    if (serviceCategory) query += `&service=${encodeURIComponent(serviceCategory)}`;
    if (searchKeyword) query += `&query=${encodeURIComponent(searchKeyword)}`;
    return await request(query);
  } catch (error) {
    await delay();
    let providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
    
    // Sort / Filter logic in Mock
    providers = providers.map(p => {
      const dist = calculateDistance(lat, lon, p.lat, p.lon);
      return { ...p, distance: dist };
    });

    // Match district filter (or show nearby)
    if (district) {
      // Keep only providers in district or nearby
      // In a real app, nearby calculations will fetch everything within a certain radius.
      // For mock: prioritize exact district first, then sort by distance.
    }

    if (serviceCategory) {
      providers = providers.filter(p => p.serviceType === serviceCategory);
    }

    if (searchKeyword) {
      const keyword = searchKeyword.toLowerCase();
      providers = providers.filter(p => 
        p.name.toLowerCase().includes(keyword) || 
        p.description.toLowerCase().includes(keyword) ||
        p.address.toLowerCase().includes(keyword)
      );
    }

    // Sort closest first
    providers.sort((a, b) => a.distance - b.distance);

    return providers;
  }
}

export async function fetchProviderDetails(providerId) {
  try {
    return await request(`/api/provider/${providerId}`);
  } catch (error) {
    await delay();
    const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
    const provider = providers.find(p => p.id === providerId);
    if (!provider) throw new Error('Provider not found');

    const reviews = JSON.parse(localStorage.getItem(MOCK_REVIEWS_KEY));
    const providerReviews = reviews.filter(r => r.providerId === providerId);

    return {
      ...provider,
      reviews: providerReviews
    };
  }
}

export async function submitReview(providerId, rating, comment) {
  const sessionUser = JSON.parse(localStorage.getItem('laso_session_user'));
  if (!sessionUser) throw new Error('Unauthorized');

  try {
    // Member 5 endpoint: /api/review
    return await request('/api/review', {
      method: 'POST',
      body: JSON.stringify({
        provider_id: providerId,
        customer_id: sessionUser.userId,
        rating,
        comment
      })
    });
  } catch (error) {
    await delay();
    const reviews = JSON.parse(localStorage.getItem(MOCK_REVIEWS_KEY));
    const newReview = {
      id: 'r' + (reviews.length + 1),
      providerId,
      customerName: sessionUser.name,
      rating: parseFloat(rating),
      comment,
      date: new Date().toISOString().split('T')[0]
    };
    reviews.push(newReview);
    localStorage.setItem(MOCK_REVIEWS_KEY, JSON.stringify(reviews));

    // Update provider average rating
    const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
    const provider = providers.find(p => p.id === providerId);
    if (provider) {
      const pReviews = reviews.filter(r => r.providerId === providerId);
      const sum = pReviews.reduce((acc, curr) => acc + curr.rating, 0);
      provider.avgRating = parseFloat((sum / pReviews.length).toFixed(1));
      provider.reviewsCount = pReviews.length;
      localStorage.setItem(MOCK_PROVIDERS_KEY, JSON.stringify(providers));
    }

    return newReview;
  }
}

export async function fetchProviderProfile(providerId) {
  try {
    return await request(`/api/provider/profile?id=${providerId}`);
  } catch (error) {
    await delay();
    const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
    const provider = providers.find(p => p.id === providerId);
    if (!provider) throw new Error('Profile not found');
    return provider;
  }
}

export async function updateProviderProfile(providerId, profileData) {
  try {
    return await request(`/api/provider/profile/update`, {
      method: 'POST',
      body: JSON.stringify({ id: providerId, ...profileData })
    });
  } catch (error) {
    await delay();
    // Update provider details in both lists
    const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY));
    const pIdx = providers.findIndex(p => p.id === providerId);
    if (pIdx !== -1) {
      providers[pIdx] = { ...providers[pIdx], ...profileData };
      localStorage.setItem(MOCK_PROVIDERS_KEY, JSON.stringify(providers));
    }

    const users = JSON.parse(localStorage.getItem(MOCK_USERS_KEY));
    const uIdx = users.findIndex(u => u.id === providerId);
    if (uIdx !== -1) {
      users[uIdx] = { ...users[uIdx], ...profileData };
      localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users));
      
      // Update session storage if modifying active provider
      const sessionUser = JSON.parse(localStorage.getItem('laso_session_user'));
      if (sessionUser && sessionUser.userId === providerId) {
        sessionUser.district = profileData.district || sessionUser.district;
        sessionUser.address = profileData.address || sessionUser.address;
        localStorage.setItem('laso_session_user', JSON.stringify(sessionUser));
      }
    }

    return { success: true };
  }
}

export async function fetchConversations(userId) {
  try {
    // Member 4 endpoint
    return await request(`/api/conversations?user_id=${userId}`);
  } catch (error) {
    await delay();
    const messages = JSON.parse(localStorage.getItem(MOCK_MESSAGES_KEY)) || [];
    const users = JSON.parse(localStorage.getItem(MOCK_USERS_KEY)) || [];
    const providers = JSON.parse(localStorage.getItem(MOCK_PROVIDERS_KEY)) || [];
    
    // Find all users this user has chatted with
    const chatPartners = new Set();
    messages.forEach(m => {
      if (m.senderId === userId) chatPartners.add(m.receiverId);
      if (m.receiverId === userId) chatPartners.add(m.senderId);
    });

    const conversations = [];
    chatPartners.forEach(partnerId => {
      // Find partner name
      const partnerUser = users.find(u => u.id === partnerId) || providers.find(p => p.id === partnerId);
      const partnerName = partnerUser ? partnerUser.name : 'Unknown User';
      const partnerService = partnerUser && partnerUser.serviceType ? partnerUser.serviceType : '';

      // Get last message
      const thread = messages.filter(m => 
        (m.senderId === userId && m.receiverId === partnerId) ||
        (m.senderId === partnerId && m.receiverId === userId)
      );
      thread.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      
      if (thread.length > 0) {
        conversations.push({
          partnerId,
          partnerName,
          partnerService,
          lastMessage: thread[0].text,
          timestamp: thread[0].timestamp
        });
      }
    });

    // Sort by recent message first
    conversations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    return conversations;
  }
}

export async function fetchMessageThread(userId, partnerId) {
  try {
    return await request(`/api/messages/thread?user_id=${userId}&partner_id=${partnerId}`);
  } catch (error) {
    await delay();
    const messages = JSON.parse(localStorage.getItem(MOCK_MESSAGES_KEY)) || [];
    const thread = messages.filter(m => 
      (m.senderId === userId && m.receiverId === partnerId) ||
      (m.senderId === partnerId && m.receiverId === userId)
    );
    thread.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    return thread;
  }
}

export async function sendMessage(senderId, receiverId, text) {
  try {
    // Member 4 endpoint: /api/message
    return await request('/api/message', {
      method: 'POST',
      body: JSON.stringify({ sender_id: senderId, receiver_id: receiverId, message: text })
    });
  } catch (error) {
    await delay(100);
    const messages = JSON.parse(localStorage.getItem(MOCK_MESSAGES_KEY)) || [];
    const newMsg = {
      id: 'm' + (messages.length + 1),
      senderId,
      receiverId,
      text,
      timestamp: new Date().toISOString()
    };
    messages.push(newMsg);
    localStorage.setItem(MOCK_MESSAGES_KEY, JSON.stringify(messages));
    return newMsg;
  }
}
