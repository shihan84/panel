<template>
  <div class="client-dashboard">
    <h2>My Streams</h2>
    <div v-if="isLoading">Loading your streams...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="!selectedStream">
      <div v-if="streams.length > 0">
        <ul>
          <li v-for="stream in streams" :key="stream.name">
            <h3>{{ stream.name }}</h3>
            <p>on Server: {{ stream.server_name }}</p>
            
            <div class="stream-details">
              <button @click="selectStream(stream)">View Details</button>
            </div>
          </li>
        </ul>
      </div>
      <p v-else-if="!isLoading">You have not been assigned any streams yet.</p>
    </div>

    <!-- Stream Details View -->
    <stream-details
      v-if="selectedStream"
      :stream="selectedStream"
      @close="selectedStream = null"
    />

  </div>
</template>

<script>
import axios from 'axios';
import StreamDetails from './StreamDetails.vue';

export default {
  components: {
    StreamDetails
  },
  data() {

    return {
      streams: [],
      isLoading: false,
      error: null,
      selectedStream: null
    };
  },
  methods: {
    async fetchMyStreams() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/client/my-streams');
        this.streams = response.data;
      } catch (err) {
        this.error = 'Failed to load your streams. Please try again later.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },
    selectStream(stream) {
      this.selectedStream = stream;
    }

  },
  mounted() {
    this.fetchMyStreams();
  }
};
</script>

<style scoped>
.client-dashboard {
  padding: 20px;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 5px;
}
.error {
  color: red;
}
</style>
