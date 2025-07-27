<template>
  <div id="app">
    <!-- Broadcast Header -->
    <header class="broadcast-header" v-if="$route.path !== '/'">
      <div class="header-content">
        <div class="logo-section">
          <div class="broadcast-logo">
            <div class="signal-icon">📡</div>
            <h1>Flussonic Dashboard</h1>
          </div>
          <div class="live-indicator">
            <span class="live-dot"></span>
            <span>LIVE</span>
          </div>
        </div>
        
        <nav class="main-nav" v-if="$store.state.user">
          <router-link to="/admin/servers" v-if="$store.state.user.isAdmin" class="nav-item">
            <span class="nav-icon">🖥️</span>
            Servers
          </router-link>
          <router-link to="/client/dashboard" v-if="!$store.state.user.isAdmin" class="nav-item">
            <span class="nav-icon">📊</span>
            Dashboard
          </router-link>
          <button @click="logout" class="nav-item logout-btn">
            <span class="nav-icon">🚪</span>
            Logout
          </button>
        </nav>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="main-content" :class="{ 'with-header': $route.path !== '/' }">
      <router-view/>
    </main>

    <!-- Broadcast Footer -->
    <footer class="broadcast-footer" v-if="$route.path !== '/'">
      <div class="footer-content">
        <div class="status-bar">
          <div class="status-item">
            <span class="status-icon">🌐</span>
            <span>Server: {{ serverStatus }}</span>
          </div>
          <div class="status-item">
            <span class="status-icon">⏰</span>
            <span>{{ currentTime }}</span>
          </div>
          <div class="status-item">
            <span class="status-icon">👤</span>
            <span v-if="$store.state.user">{{ $store.state.user.username }}</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentTime: '',
      serverStatus: 'Online',
      timeInterval: null
    }
  },
  mounted() {
    this.updateTime();
    this.timeInterval = setInterval(this.updateTime, 1000);
  },
  beforeUnmount() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  },
  methods: {
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleTimeString();
    },
    logout() {
      this.$store.commit('clearAuth');
      this.$router.push('/');
    }
  }
}
</script>

<style>
/* Global Broadcast Theme Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #0f1419 100%);
  min-height: 100vh;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* Broadcast Header */
.broadcast-header {
  background: linear-gradient(90deg, #1e3a5f 0%, #2d5a87 50%, #1e3a5f 100%);
  border-bottom: 3px solid #00d4ff;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.broadcast-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.signal-icon {
  font-size: 2rem;
  animation: pulse 2s infinite;
}

.broadcast-logo h1 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(45deg, #00d4ff, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #ff4444;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
  box-shadow: 0 2px 10px rgba(255, 68, 68, 0.4);
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #ffffff;
  border-radius: 50%;
  animation: blink 1s infinite;
}

/* Navigation */
.main-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.nav-item:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}

.nav-item.router-link-active {
  background: linear-gradient(45deg, #00d4ff, #0099cc);
  border-color: #00d4ff;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.logout-btn {
  background: rgba(255, 68, 68, 0.2) !important;
  border-color: rgba(255, 68, 68, 0.5) !important;
}

.logout-btn:hover {
  background: rgba(255, 68, 68, 0.3) !important;
  border-color: #ff4444 !important;
}

.nav-icon {
  font-size: 1.1rem;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content.with-header {
  padding-top: 2rem;
}

/* Broadcast Footer */
.broadcast-footer {
  background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
  border-top: 2px solid #00d4ff;
  margin-top: auto;
}

.footer-content {
  padding: 1rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #cccccc;
}

.status-icon {
  font-size: 1rem;
}

/* Animations */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .logo-section {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .main-nav {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .status-bar {
    justify-content: center;
    text-align: center;
  }
  
  .main-content {
    padding: 1rem;
  }
}

/* Broadcast Theme Utilities */
.broadcast-card {
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.8) 0%, rgba(45, 90, 135, 0.8) 100%);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.broadcast-card:hover {
  border-color: #00d4ff;
  box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
  transform: translateY(-4px);
}

.broadcast-button {
  background: linear-gradient(45deg, #00d4ff, #0099cc);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}

.broadcast-button:hover {
  background: linear-gradient(45deg, #0099cc, #007399);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.broadcast-button:active {
  transform: translateY(0);
}

.broadcast-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  padding: 0.75rem;
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.broadcast-input:focus {
  outline: none;
  border-color: #00d4ff;
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

.broadcast-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}
</style>
