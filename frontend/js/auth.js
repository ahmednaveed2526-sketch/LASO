import { loginUser, registerUser } from './api.js';
import { DISTRICTS, setSessionUser, getQueryParams } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
  // Check which page we are on
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const userTypeSelectContainer = document.getElementById('user-type-select-container');

  if (loginForm) {
    handleLoginForm(loginForm);
  }

  if (registerForm) {
    handleRegisterForm(registerForm);
  }
});

function handleLoginForm(form) {
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const errorAlert = document.getElementById('error-alert');
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorAlert.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    try {
      const sessionData = await loginUser(email, password);
      setSessionUser(sessionData);

      // Redirect to correct dashboard
      if (sessionData.userType === 'customer') {
        window.location.href = '../customer/dashboard.html';
      } else {
        window.location.href = '../provider/dashboard.html';
      }
    } catch (err) {
      errorAlert.textContent = err.message || 'Login failed. Try again.';
      errorAlert.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Log In';
    }
  });
}

function handleRegisterForm(form) {
  const params = getQueryParams();
  const userType = params.type || 'customer'; // default

  // Setup Title and Fields Visibility
  const pageTitle = document.getElementById('register-title');
  if (pageTitle) {
    pageTitle.textContent = userType === 'customer' ? 'Customer Signup' : 'Provider Signup';
  }

  const providerFields = document.getElementById('provider-only-fields');
  if (providerFields) {
    providerFields.style.display = userType === 'provider' ? 'block' : 'none';
  }

  // Handle district coordinates autofill
  const districtSelect = document.getElementById('district');
  const latInput = document.getElementById('lat');
  const lonInput = document.getElementById('lon');

  if (districtSelect) {
    districtSelect.addEventListener('change', () => {
      const district = districtSelect.value;
      if (district && DISTRICTS[district]) {
        latInput.value = DISTRICTS[district].lat;
        lonInput.value = DISTRICTS[district].lon;
      }
    });
  }

  // Handle GPS Location Retrieval
  const gpsBtn = document.getElementById('btn-gps');
  if (gpsBtn) {
    gpsBtn.addEventListener('click', () => {
      gpsBtn.disabled = true;
      gpsBtn.textContent = '⌛ Fetching...';
      
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            latInput.value = position.coords.latitude.toFixed(6);
            lonInput.value = position.coords.longitude.toFixed(6);
            gpsBtn.disabled = false;
            gpsBtn.textContent = '🎯 Location Captured';
            setTimeout(() => { gpsBtn.textContent = '🎯 Get Current GPS'; }, 2000);
          },
          (error) => {
            alert('Unable to retrieve GPS. Fallback coordinates of selected district will be used.');
            gpsBtn.disabled = false;
            gpsBtn.textContent = '❌ Try Again';
          },
          { enableHighAccuracy: true, timeout: 5000 }
        );
      } else {
        alert('Geolocation not supported by this browser.');
        gpsBtn.disabled = false;
        gpsBtn.textContent = '❌ Not Supported';
      }
    });
  }

  // Handle Signup submission
  const errorAlert = document.getElementById('error-alert');
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorAlert.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const district = document.getElementById('district').value;
    const address = document.getElementById('address').value.trim();

    const userData = {
      name,
      email,
      phone,
      password,
      district,
      address,
      userType
    };

    if (userType === 'provider') {
      userData.serviceType = document.getElementById('service-type').value;
      userData.lat = parseFloat(latInput.value || DISTRICTS[district]?.lat || 0);
      userData.lon = parseFloat(lonInput.value || DISTRICTS[district]?.lon || 0);
      userData.description = document.getElementById('description').value.trim();
      
      if (!userData.serviceType) {
        alert('Please select a service type.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        return;
      }
    }

    try {
      const sessionData = await registerUser(userData);
      setSessionUser(sessionData);
      
      // Redirect to correct dashboard
      if (userType === 'customer') {
        window.location.href = '../customer/dashboard.html';
      } else {
        window.location.href = '../provider/dashboard.html';
      }
    } catch (err) {
      errorAlert.textContent = err.message || 'Registration failed. Try again.';
      errorAlert.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Register';
    }
  });
}
