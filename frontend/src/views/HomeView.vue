<template>
  <div class="home">
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
              class="form-control"
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
              class="form-control"
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
              class="form-control"
              style="text-transform: uppercase"
              required
            />
          </div>

          <div class="modal-actions">
            <button
              type="submit"
              class="btn btn-primary btn-lg"
              :disabled="processing"
            >
              <span v-if="processing" class="loading-spinner" aria-hidden="true"></span>
              {{ processing ? 'Processing...' : modalMode === 'create' ? 'Create Event' : 'Join Event' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-outline">Cancel</button>
          </div>
        </form>

        <p v-if="modalError" class="error">{{ modalError }}</p>
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
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-8) var(--spacing-4);
  max-width: 900px;
  margin: 0 auto;
  min-height: calc(100vh - 2 * var(--spacing-8));
}

.action-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-8);
  width: 100%;
}

.action-card {
  background: var(--color-surface);
  padding: var(--spacing-8);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--color-border-hover);
}

.action-card h3 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
}

.action-card p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-6);
  line-height: var(--line-height-relaxed);
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
  .action-section {
    grid-template-columns: 1fr;
    gap: var(--spacing-6);
  }

  .action-card {
    padding: var(--spacing-6);
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
