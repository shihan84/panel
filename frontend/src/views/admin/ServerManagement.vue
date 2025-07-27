<template>
  <div class="server-management">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>🖥️ Server Management</h1>
          <p>Manage your Flussonic media servers and monitor streaming infrastructure</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-number">{{ servers.length }}</div>
              <div class="stat-label">Servers</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📺</div>
            <div class="stat-info">
              <div class="stat-number">{{ totalStreams }}</div>
              <div class="stat-label">Streams</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Server Section -->
    <div class="broadcast-card add-server-section">
      <div class="section-header">
        <h2>➕ Add New Server</h2>
        <p>Connect a new Flussonic media server to your dashboard</p>
      </div>

      <form @submit.prevent="addServer" class="server-form">
        <div class="form-row">
          <div class="form-group">
            <label for="serverName">
              <span class="label-icon">🏷️</span>
              Server Name
            </label>
            <input 
              id="serverName"
              v-model="newServer.name" 
              class="broadcast-input"
              placeholder="e.g., Main Streaming Server" 
              required 
            />
          </div>
          <div class="form-group">
            <label for="serverUrl">
              <span class="label-icon">🌐</span>
              Server URL
            </label>
            <input 
              id="serverUrl"
              v-model="newServer.url" 
              class="broadcast-input"
              placeholder="http://your-server:8080" 
              required 
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="serverUsername">
              <span class="label-icon">👤</span>
              Username
            </label>
            <input 
              id="serverUsername"
              v-model="newServer.username" 
              class="broadcast-input"
              placeholder="Admin username" 
              required 
            />
          </div>
          <div class="form-group">
            <label for="serverPassword">
              <span class="label-icon">🔑</span>
              Password
            </label>
            <input 
              id="serverPassword"
              v-model="newServer.password" 
              type="password" 
              class="broadcast-input"
              placeholder="Admin password" 
              required 
            />
          </div>
        </div>

        <button type="submit" class="broadcast-button add-server-btn" :disabled="isAddingServer">
          <span v-if="!isAddingServer" class="button-content">
            <span class="button-icon">🚀</span>
            Add Server
          </span>
          <span v-else class="loading-content">
            <span class="spinner"></span>
            Adding Server...
          </span>
        </button>
      </form>
    </div>

    <!-- Servers List -->
    <div class="servers-section">
      <div class="section-header">
        <h2>📡 Connected Servers</h2>
        <p v-if="servers.length === 0">No servers connected yet. Add your first server above.</p>
        <p v-else>{{ servers.length }} server{{ servers.length !== 1 ? 's' : '' }} connected</p>
      </div>

      <div class="servers-grid" v-if="servers.length > 0">
        <div 
          v-for="server in servers" 
          :key="server.id" 
          class="server-card broadcast-card"
          :class="{ 'expanded': selectedServerId === server.id }"
        >
          <!-- Server Header -->
          <div class="server-header">
            <div class="server-info">
              <div class="server-name">
                <span class="server-icon">🖥️</span>
                {{ server.name }}
              </div>
              <div class="server-url">{{ server.url }}</div>
            </div>
            <div class="server-actions">
              <button 
                @click="getStreams(server.id)" 
                class="action-btn streams-btn"
                :disabled="isLoadingStreams"
                :class="{ 'active': selectedServerId === server.id }"
              >
                <span class="btn-icon">📺</span>
                <span v-if="selectedServerId !== server.id">View Streams</span>
                <span v-else>Hide Streams</span>
              </button>
              <button 
                @click="testConnection(server.id)" 
                class="action-btn test-btn"
                :disabled="isTestingConnection"
              >
                <span class="btn-icon">🔍</span>
                Test
              </button>
            </div>
          </div>

          <!-- Server Status -->
          <div class="server-status">
            <div class="status-indicator" :class="getServerStatus(server.id)">
              <span class="status-dot"></span>
              <span class="status-text">{{ getServerStatusText(server.id) }}</span>
            </div>
            <div class="last-checked">
              Last checked: {{ getLastChecked(server.id) }}
            </div>
          </div>

          <!-- Streams Section -->
          <div v-if="selectedServerId === server.id" class="streams-section">
            <div class="streams-header">
              <h4>📺 Streams</h4>
              <button @click="closeStreamsView" class="close-btn">✕</button>
            </div>

            <div v-if="isLoadingStreams" class="loading-state">
              <div class="spinner-large"></div>
              <p>Loading streams...</p>
            </div>

            <div v-else-if="streamsError" class="error-state">
              <div class="error-icon">⚠️</div>
              <div class="error-content">
                <h5>Failed to load streams</h5>
                <p>{{ streamsError }}</p>
                <button @click="getStreams(server.id)" class="retry-btn">
                  🔄 Retry
                </button>
              </div>
            </div>

            <div v-else-if="streams.length === 0" class="empty-state">
              <div class="empty-icon">📭</div>
              <h5>No streams found</h5>
              <p>This server doesn't have any active streams</p>
            </div>

            <div v-else class="streams-list">
              <div 
                v-for="stream in streams" 
                :key="stream.name" 
                class="stream-item"
              >
                <div class="stream-info">
                  <div class="stream-name">
                    <span class="stream-icon">🎬</span>
                    {{ stream.name }}
                  </div>
                  <div class="stream-details">
                    <span class="stream-status" :class="stream.status || 'unknown'">
                      {{ stream.status || 'Unknown' }}
                    </span>
                    <span class="stream-viewers" v-if="stream.viewers">
                      👥 {{ stream.viewers }} viewers
                    </span>
                  </div>
                </div>
                <div class="stream-actions">
                  <button class="stream-action-btn" title="View Details">
                    📊
                  </button>
                  <button class="stream-action-btn" title="Monitor">
                    👁️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ServerManagement',
  data() {
    return {
      newServer: {
        name: '',
        url: '',
        username: '',
        password: ''
      },
      servers: [],
      selectedServerId: null,
      streams: [],
      isLoadingStreams: false,
      isAddingServer: false,
      isTestingConnection: false,
      streamsError: null,
      serverStatuses: {},
      lastCheckedTimes: {}
    };
  },
  computed: {
    totalStreams() {
      return this.streams.length;
    }
  },
  methods: {
    async fetchServers() {
      try {
        const response = await axios.get('/api/admin/servers');
        this.servers = response.data;
        // Initialize server statuses
        this.servers.forEach(server => {
          if (!this.serverStatuses[server.id]) {
            this.serverStatuses[server.id] = 'unknown';
            this.lastCheckedTimes[server.id] = 'Never';
          }
        });
      } catch (error) {
        console.error("Error fetching servers:", error);
      }
    },

    async addServer() {
      this.isAddingServer = true;
      try {
        await axios.post('/api/admin/servers', this.newServer);
        this.newServer = { name: '', url: '', username: '', password: '' };
        await this.fetchServers();
        this.showNotification('Server added successfully!', 'success');
      } catch (error) {
        console.error("Error adding server:", error);
        this.showNotification(
          error.response?.data?.detail || 'Failed to add server. Please check your connection and try again.',
          'error'
        );
      } finally {
        this.isAddingServer = false;
      }
    },

    async getStreams(serverId) {
      if (this.selectedServerId === serverId) {
        this.closeStreamsView();
        return;
      }

      this.selectedServerId = serverId;
      this.isLoadingStreams = true;
      this.streams = [];
      this.streamsError = null;

      try {
        const response = await axios.get(`/api/admin/servers/${serverId}/streams`);
        this.streams = response.data;
        this.serverStatuses[serverId] = 'online';
        this.lastCheckedTimes[serverId] = new Date().toLocaleTimeString();
      } catch (error) {
        console.error(`Error fetching streams for server ${serverId}:`, error);
        this.streamsError = error.response?.data?.detail || 'Failed to fetch streams.';
        this.serverStatuses[serverId] = 'offline';
        this.lastCheckedTimes[serverId] = new Date().toLocaleTimeString();
      } finally {
        this.isLoadingStreams = false;
      }
    },

    async testConnection(serverId) {
      this.isTestingConnection = true;
      try {
        // Test connection by trying to fetch server info
        await axios.get(`/api/admin/servers/${serverId}/streams`);
        this.serverStatuses[serverId] = 'online';
        this.lastCheckedTimes[serverId] = new Date().toLocaleTimeString();
        this.showNotification('Connection test successful!', 'success');
      } catch (error) {
        this.serverStatuses[serverId] = 'offline';
        this.lastCheckedTimes[serverId] = new Date().toLocaleTimeString();
        this.showNotification('Connection test failed!', 'error');
      } finally {
        this.isTestingConnection = false;
      }
    },

    closeStreamsView() {
      this.selectedServerId = null;
      this.streams = [];
      this.streamsError = null;
    },

    getServerStatus(serverId) {
      return this.serverStatuses[serverId] || 'unknown';
    },

    getServerStatusText(serverId) {
      const status = this.serverStatuses[serverId] || 'unknown';
      const statusTexts = {
        online: 'Online',
        offline: 'Offline',
        unknown: 'Unknown'
      };
      return statusTexts[status];
    },

    getLastChecked(serverId) {
      return this.lastCheckedTimes[serverId] || 'Never';
    },

    showNotification(message, type) {
      // Simple notification system - you can enhance this
      const notification = document.createElement('div');
      notification.className = `notification ${type}`;
      notification.textContent = message;
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#00ff88' : '#ff4444'};
      `;
      
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.remove();
      }, 3000);
    }
  },

  mounted() {
    this.fetchServers();
  }
};
</script>

<style scoped>
.server-management {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-title h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(45deg, #00d4ff, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-title p {
  color: #cccccc;
  font-size: 1.1rem;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  min-width: 120px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #00d4ff;
}

.stat-label {
  font-size: 0.9rem;
  color: #cccccc;
}

/* Add Server Section */
.add-server-section {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.section-header p {
  color: #cccccc;
}

.server-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
}

.label-icon {
  font-size: 1.1rem;
}

.add-server-btn {
  align-self: flex-start;
  min-width: 200px;
}

/* Servers Section */
.servers-section {
  margin-bottom: 2rem;
}

.servers-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
}

.server-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.server-card.expanded {
  grid-column: 1 / -1;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.server-info {
  flex: 1;
}

.server-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.3rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.server-icon {
  font-size: 1.5rem;
}

.server-url {
  color: #00d4ff;
  font-size: 0.9rem;
  font-family: monospace;
}

.server-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  color: #ffffff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}

.action-btn.active {
  background: linear-gradient(45deg, #00d4ff, #0099cc);
  border-color: #00d4ff;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1rem;
}

/* Server Status */
.server-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.online .status-dot {
  background: #00ff88;
}

.status-indicator.offline .status-dot {
  background: #ff4444;
}

.status-indicator.unknown .status-dot {
  background: #ffaa00;
}

.status-text {
  font-weight: 600;
}

.last-checked {
  font-size: 0.8rem;
  color: #cccccc;
}

/* Streams Section */
.streams-section {
  border-top: 1px solid rgba(0, 212, 255, 0.3);
  padding-top: 1rem;
  margin-top: 1rem;
}

.streams-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.streams-header h4 {
  color: #ffffff;
  font-size: 1.2rem;
}

.close-btn {
  background: rgba(255, 68, 68, 0.2);
  border: 1px solid rgba(255, 68, 68, 0.5);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 68, 68, 0.3);
  border-color: #ff4444;
}

/* Loading, Error, and Empty States */
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 212, 255, 0.3);
  border-top: 3px solid #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-state {
  color: #ff6b6b;
}

.error-icon, .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-content h5, .empty-state h5 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.retry-btn {
  background: linear-gradient(45deg, #ff6b6b, #ff4444);
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  color: #ffffff;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: linear-gradient(45deg, #ff4444, #cc3333);
}

/* Streams List */
.streams-list {
  display: grid;
  gap: 0.75rem;
}

.stream-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stream-item:hover {
  border-color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
}

.stream-info {
  flex: 1;
}

.stream-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.stream-icon {
  font-size: 1.2rem;
}

.stream-details {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.stream-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.stream-status.active {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.stream-status.inactive {
  background: rgba(255, 68, 68, 0.2);
  color: #ff6b6b;
}

.stream-status.unknown {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.stream-viewers {
  color: #cccccc;
}

.stream-actions {
  display: flex;
  gap: 0.5rem;
}

.stream-action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 4px;
  padding: 0.5rem;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.stream-action-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}

/* Loading Content */
.button-content, .loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-stats {
    width: 100%;
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .servers-grid {
    grid-template-columns: 1fr;
  }
  
  .server-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .server-actions {
    width: 100%;
    justify-content: center;
  }
  
  .stream-item {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .stream-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
