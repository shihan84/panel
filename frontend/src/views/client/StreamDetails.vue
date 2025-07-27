<template>
  <div class="stream-details-view">
    <button @click="$emit('close')">Back to Dashboard</button>
    <h2>Details for {{ stream.name }}</h2>
    
    <!-- Stream Preview -->
    <div class="detail-section">
      <h3>Live Preview</h3>
      <!-- A real video player (like video.js or Shaka Player) would be integrated here -->
      <div class="video-placeholder">
        <p>Live video player for {{ stream.name }} would be here.</p>
        <p>(Server: {{ stream.server_name }})</p>
      </div>
    </div>

    <!-- Traffic Usage -->
    <div class="detail-section">
      <h3>Traffic Usage (Last 30 Days)</h3>
      <!-- A chart component (like Chart.js) would be integrated here -->
      <div v-if="isTrafficLoading">Loading traffic data...</div>
      <div v-if="trafficError" class="error">{{ trafficError }}</div>
      <div class="chart-placeholder" v-if="!isTrafficLoading && trafficData.length > 0">
        <p>Traffic chart would be displayed here.</p>
        <ul>
          <li v-for="record in trafficData" :key="record.timestamp">
            {{ record.timestamp }}: {{ (record.bytes_used / 1024 / 1024 / 1024).toFixed(2) }} GB
          </li>
        </ul>
      </div>
       <p v-if="!isTrafficLoading && trafficData.length === 0">No traffic data available for the selected period.</p>
    </div>

    <!-- Push Destinations -->
    <div class="detail-section">
      <h3>Restream (Push) Destinations</h3>
      <div v-if="isPushesLoading">Loading push destinations...</div>
      <div v-if="pushesError" class="error">{{ pushesError }}</div>
      <ul>
        <li v-for="push in pushes" :key="push.url">
          <span>{{ push.url }}</span>
          <button @click="removePush(push.url)">Remove</button>
        </li>
      </ul>
      <form @submit.prevent="addPush">
        <input v-model="newPushUrl" placeholder="rtmp://a.rtmp.youtube.com/live2" required />
        <button type="submit">Add Push URL</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { onMounted, ref } from 'vue';

export default {
  props: {
    stream: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    const trafficData = ref([]);
    const isTrafficLoading = ref(false);
    const trafficError = ref(null);

    const pushes = ref([]);
    const isPushesLoading = ref(false);
    const pushesError = ref(null);
    const newPushUrl = ref('');

    const fetchTrafficData = async () => {
      isTrafficLoading.value = true;
      trafficError.value = null;
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - 30);

      try {
        const response = await axios.get(`/api/client/${props.stream.name}/traffic`, {
          params: {
            start_date: startDate.toISOString().split('T')[0],
            end_date: endDate.toISOString().split('T')[0],
          }
        });
        trafficData.value = response.data;
      } catch (error) {
        trafficError.value = 'Failed to load traffic data.';
        console.error(error);
      } finally {
        isTrafficLoading.value = false;
      }
    };

    const fetchPushes = async () => {
        isPushesLoading.value = true;
        pushesError.value = null;
        try {
            const response = await axios.get(`/api/client/${props.stream.name}/pushes`);
            pushes.value = response.data;
        } catch (error) {
            pushesError.value = 'Failed to load push destinations.';
            console.error(error);
        } finally {
            isPushesLoading.value = false;
        }
    };

    const addPush = async () => {
        if (!newPushUrl.value) return;
        try {
            await axios.post(`/api/client/${props.stream.name}/pushes`, { url: newPushUrl.value });
            newPushUrl.value = '';
            await fetchPushes(); // Refresh list
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to add push destination.');
            console.error(error);
        }
    };

    const removePush = async (url) => {
        if (!confirm(`Are you sure you want to remove the push destination: ${url}?`)) return;
        try {
            await axios.delete(`/api/client/${props.stream.name}/pushes`, { data: { url } });
            await fetchPushes(); // Refresh list
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to remove push destination.');
            console.error(error);
        }
    };

    onMounted(() => {
      fetchTrafficData();
      fetchPushes();
    });

    return {
      trafficData,
      isTrafficLoading,
      trafficError,
      pushes,
      isPushesLoading,
      pushesError,
      newPushUrl,
      addPush,
      removePush,
    };
  }
};
</script>

<style scoped>
.stream-details-view {
  padding: 20px;
  background-color: #fff;
}
.detail-section {
  margin-bottom: 30px;
}
.video-placeholder, .chart-placeholder {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  background-color: #f0f0f0;
  min-height: 150px;
}
</style>
