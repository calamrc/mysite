<template>
  <div class="home">
    <div class="hero">
      <h1>🎄 Gift Exchange Manager</h1>
      <p>Create secret Santa events and organize gift exchanges with friends and family</p>
    </div>

    <div class="action-section">
      <!-- Join Event -->
      <div class="action-card">
        <h3>🎁 Join an Event</h3>
        <p>Enter an event code to join an existing gift exchange</p>
        <button @click="openModal('join')" class="btn btn-primary">
          Join Event
        </button>
      </div>

      <!-- Create Event -->
      <div class="action-card">
        <h3>✨ Create New Event</h3>
        <p>Start a new gift exchange event</p>
        <button @click="openModal('create')" class="btn btn-secondary">
          Create Event
        </button>
      </div>
    </div>

    <!-- Unified PIN Modal -->
    <div v-if="showModal" class="auth-modal">
      <div class="modal-content">
        <h2>{{ modalMode === 'create' ? 'Create New Event' : 'Join Event' }}</h2>
        <p v-if="modalMode === 'join'">
          Enter the event code and PIN to join the gift exchange.
        </p>
        <p v-else>
          Choose a PIN to create your new gift exchange event.
        </p>

        <form @submit.prevent="submitModal" class="auth-form">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="modalUsername"
              type="text"
              placeholder="Enter your username"
              maxlength="50"
              required
            />
          </div>

          <div class="form-group">
            <label for="pin">PIN</label>
            <input
              id="pin"
              v-model="modalPin"
              type="password"
              placeholder="Enter PIN (4+ characters)"
              minlength="4"
              required
            />
          </div>

          <div v-if="modalMode === 'join'" class="form-group">
            <label for="eventCode">Event Code</label>
            <input
              id="eventCode"
              v-model="modalEventCode"
              type="text"
              placeholder="Enter event code (e.g., ABC123)"
              maxlength="6"
              style="text-transform: uppercase"
              required
            />
          </div>

          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="processing">
              {{ processing ? 'Processing...' : modalMode === 'create' ? 'Create Event' : 'Join Event' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>

        <p v-if="modalError" class="error">{{ modalError }}</p>
      </div>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>🎅 Secret Santa</h3>
        <p>Random assignments ensure everyone gets a gift</p>
      </div>

      <div class="feature-card">
        <h3>👥 Multiple Roles</h3>
        <p>Organizers manage events, participants join and draw</p>
      </div>

      <div class="feature-card">
        <h3>📱 Mobile Friendly</h3>
        <p>Works great on phones and tablets</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      // Modal state
      showModal: false,
      modalMode: 'create', // 'create' or 'join'
      modalUsername: '',
      modalPin: '',
      modalEventCode: '',
      processing: false,
      modalError: ''
    }
  },
  async mounted() {
    // Check if user is already authenticated
    try {
      const response = await this.$http.get('/api/auth/status', { withCredentials: true })
      if (response.data.authenticated && response.data.user) {
        const user = response.data.user
        // Redirect based on role
        if (user.role === 'organizer' && user.event_code) {
          this.$router.push(`/organizer/${user.event_code}`)
        } else if (user.role === 'participant' && user.event_code) {
          this.$router.push(`/participant/${user.event_code}`)
        }
      }
    } catch (error) {
      // Not authenticated or error, show home page normally
      console.log('User not authenticated, showing home page')
    }
  },
  methods: {
    openModal(mode) {
      this.modalMode = mode
      this.modalUsername = ''
      this.modalPin = ''
      this.modalEventCode = ''
      this.modalError = ''
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.modalUsername = ''
      this.modalPin = ''
      this.modalEventCode = ''
      this.modalError = ''
    },

    async submitModal() {
      if (this.processing) return

      this.processing = true
      this.modalError = ''

      try {
        const response = await axios.post('/api/events/join-or-create', {
          username: this.modalUsername,
          pin: this.modalPin,
          event_code: this.modalEventCode || undefined
        })

        if (response.data.success) {
          // Route based on role
          const route = response.data.role === 'organizer' ? 'organizer' : 'participant'
          this.$router.push(`/${route}/${response.data.event_code}`)
          this.closeModal()
        }
      } catch (error) {
        this.modalError = error.response?.data?.error || 'Failed to process request'
        console.error('Modal submit error:', error)
      } finally {
        this.processing = false
      }
    }
  }
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #2c3e50;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.hero p {
  font-size: 1.3rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.action-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.action-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e1e8ed;
}

.action-card h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.4rem;
}

.action-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

.action-form {
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
  text-align: center;
  font-weight: bold;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.3s;
  width: 100%;
}

.btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #2ecc71;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #27ae60;
}

.error {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: 1px solid #e1e8ed;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  color: #3498db;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: #666;
}

/* Modal Styles */
.auth-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  max-width: 400px;
  width: 90%;
}

.modal-content h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
  text-align: center;
}

.modal-content p {
  color: #666;
  margin-bottom: 1.5rem;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.auth-form {
  margin-top: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: bold;
}

.form-group input {
  text-align: left;
}

.btn {
  flex: 1;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }

  .action-section {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .action-card {
    padding: 1.5rem;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
