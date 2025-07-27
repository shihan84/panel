<template>
  <div class="login-container">
    <!-- Broadcast Login Header -->
    <div class="login-header">
      <div class="broadcast-logo-large">
        <div class="signal-icon-large">📡</div>
        <h1>Flussonic Dashboard</h1>
        <div class="tagline">Professional Broadcasting Control Center</div>
      </div>
      <div class="live-indicator-large">
        <span class="live-dot-large"></span>
        <span>SYSTEM ONLINE</span>
      </div>
    </div>

    <!-- Login Form -->
    <div class="login-card">
      <div class="login-form-header">
        <h2>🔐 Secure Access</h2>
        <p>Enter your credentials to access the broadcast control panel</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="username">
            <span class="label-icon">👤</span>
            Username
          </label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            class="broadcast-input"
            placeholder="Enter your username"
            required
          >
        </div>

        <div class="form-group">
          <label for="password">
            <span class="label-icon">🔑</span>
            Password
          </label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            class="broadcast-input"
            placeholder="Enter your password"
            required
          >
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ error }}
        </div>

        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="!isLoading" class="button-content">
            <span class="button-icon">🚀</span>
            Access Dashboard
          </span>
          <span v-else class="loading-content">
            <span class="spinner"></span>
            Authenticating...
          </span>
        </button>
      </form>

      <!-- Additional Info -->
      <div class="login-footer">
        <div class="security-info">
          <span class="security-icon">🛡️</span>
          <span>Secure SSL Connection</span>
        </div>
        <div class="version-info">
          <span>v1.0.0</span>
        </div>
      </div>
    </div>

    <!-- Background Animation -->
    <div class="background-animation">
      <div class="wave wave1"></div>
      <div class="wave wave2"></div>
      <div class="wave wave3"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: null,
      isLoading: false
    };
  },
  methods: {
    async login() {
      this.error = null;
      this.isLoading = true;

      try {
        // FastAPI's OAuth2PasswordRequestForm expects form data
        const params = new URLSearchParams();
        params.append('username', this.username);
        params.append('password', this.password);

        const response = await axios.post('/api/auth/token', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        const token = response.data.access_token;
        this.$store.commit('setToken', token);
        
        // Set default auth header for all subsequent axios requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // Decode token to check user role
        const payload = JSON.parse(atob(token.split('.')[1]));
        this.$store.commit('setUser', { username: payload.sub, isAdmin: payload.is_admin });

        // Simulate loading for better UX
        setTimeout(() => {
          if (payload.is_admin) {
            this.$router.push('/admin/servers');
          } else {
            this.$router.push('/client/dashboard');
          }
        }, 1000);

      } catch (err) {
        this.isLoading = false;
        if (err.response && err.response.data && err.response.data.detail) {
          this.error = err.response.data.detail;
        } else {
          this.error = 'Connection failed. Please check your network and try again.';
        }
        console.error("Login failed:", err);
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

/* Login Header */
.login-header {
  text-align: center;
  margin-bottom: 3rem;
  z-index: 2;
  position: relative;
}

.broadcast-logo-large {
  margin-bottom: 2rem;
}

.signal-icon-large {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

.broadcast-logo-large h1 {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(45deg, #00d4ff, #ffffff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
}

.tagline {
  font-size: 1.2rem;
  color: #cccccc;
  font-weight: 300;
  letter-spacing: 1px;
}

.live-indicator-large {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(45deg, #00ff88, #00cc6a);
  padding: 0.75rem 2rem;
  border-radius: 30px;
  font-weight: bold;
  font-size: 1rem;
  box-shadow: 0 4px 20px rgba(0, 255, 136, 0.4);
  animation: glow 2s ease-in-out infinite alternate;
}

.live-dot-large {
  width: 12px;
  height: 12px;
  background: #ffffff;
  border-radius: 50%;
  animation: blink 1s infinite;
}

/* Login Card */
.login-card {
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.95) 0%, rgba(45, 90, 135, 0.95) 100%);
  border: 2px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 2;
}

.login-form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-form-header h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.login-form-header p {
  color: #cccccc;
  font-size: 1rem;
}

/* Form Styles */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #ffffff;
  font-size: 1rem;
}

.label-icon {
  font-size: 1.1rem;
}

.broadcast-input {
  padding: 1rem;
  font-size: 1rem;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.broadcast-input:focus {
  transform: translateY(-2px);
}

/* Login Button */
.login-button {
  background: linear-gradient(45deg, #00d4ff, #0099cc);
  border: none;
  border-radius: 12px;
  padding: 1rem 2rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
  margin-top: 1rem;
  position: relative;
  overflow: hidden;
}

.login-button:hover:not(:disabled) {
  background: linear-gradient(45deg, #0099cc, #007399);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5);
}

.login-button:active {
  transform: translateY(-1px);
}

.login-button:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.button-content, .loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.button-icon {
  font-size: 1.2rem;
}

/* Loading Spinner */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 68, 68, 0.2);
  border: 1px solid rgba(255, 68, 68, 0.5);
  border-radius: 8px;
  padding: 1rem;
  color: #ff6b6b;
  font-weight: 500;
}

.error-icon {
  font-size: 1.2rem;
}

/* Login Footer */
.login-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
  color: #cccccc;
}

.security-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.security-icon {
  color: #00ff88;
}

/* Background Animation */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.wave {
  position: absolute;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, rgba(0, 212, 255, 0.1), rgba(0, 153, 204, 0.1));
  border-radius: 50%;
  animation: wave 20s linear infinite;
}

.wave1 {
  top: -50%;
  left: -50%;
  animation-delay: 0s;
}

.wave2 {
  top: -60%;
  left: -60%;
  animation-delay: -5s;
  background: linear-gradient(45deg, rgba(0, 255, 136, 0.1), rgba(0, 204, 106, 0.1));
}

.wave3 {
  top: -70%;
  left: -70%;
  animation-delay: -10s;
  background: linear-gradient(45deg, rgba(255, 68, 68, 0.1), rgba(204, 54, 54, 0.1));
}

@keyframes wave {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes glow {
  from { box-shadow: 0 4px 20px rgba(0, 255, 136, 0.4); }
  to { box-shadow: 0 4px 30px rgba(0, 255, 136, 0.6); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
  }
  
  .broadcast-logo-large h1 {
    font-size: 2rem;
  }
  
  .signal-icon-large {
    font-size: 3rem;
  }
  
  .login-card {
    padding: 2rem;
  }
  
  .login-footer {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>
