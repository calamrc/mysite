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

        <div class="username-input-group">
          <div class="input-wrapper">
            <input
              id="username"
              v-model="modalUsername"
              type="text"
              placeholder="Enter your username"
              maxlength="50"
              class="form-control username-input"
              required
            />
            <button
              type="button"
              @click="regenerateUsername"
              class="refresh-btn"
              aria-label="Generate random username"
            >
              <span class="refresh-icon">🔄</span>
            </button>
          </div>
        </div>

        <form @submit.prevent="submitModal" class="auth-form">
          <div class="form-group">
            <input
              id="pin"
              v-model="modalPin"
              type="password"
              placeholder="PIN (4+ characters)"
              minlength="4"
              class="form-control"
              required
            />
          </div>

          <div v-if="modalMode === 'join'" class="form-group">
            <input
              id="eventCode"
              v-model="modalEventCode"
              type="text"
              placeholder="Enter event code (e.g., ABC123)"
              maxlength="6"
              class="form-control"
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
      modalError: '',
      // Username words for random generation
      usernameWords: [
        'Phoenix', 'Blizzard', 'Thunder', 'Whisper', 'Eclipse', 'Mystic', 'Tempest',
        'Sapphire', 'Crimson', 'Aurora', 'Storm', 'Jester', 'Nova', 'Specter', 'Radiant',
        'Vortex', 'Harmony', 'Falcon', 'Trinity', 'Orion', 'Lunar', 'Zenith', 'Cascade',
        'Brave', 'Courage', 'Justice', 'Liberty', 'Spirit', 'Wisdom', 'Passion', 'Dream',
        'Cosmic', 'Galactic', 'Eternal', 'Infinite', 'Majestic', 'Noble', 'Royal', 'Flame',
        'Frost', 'Shadow', 'Light', 'Star', 'Moon', 'Sun', 'Wind', 'Earth', 'Fire', 'Water'
      ]
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
      this.modalPin = ''
      this.modalEventCode = ''
      this.modalError = ''
      this.regenerateUsername() // Generate initial username
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.modalUsername = ''
      this.modalPin = ''
      this.modalEventCode = ''
      this.modalError = ''
    },

    regenerateUsername() {
      // Randomly select from the username words list
      const randomWord = this.usernameWords[Math.floor(Math.random() * this.usernameWords.length)]
      this.modalUsername = randomWord
    },

    async submitModal() {
      if (this.processing) return

      this.processing = true
      this.modalError = ''

      try {
        // Prepare request data based on mode
        const requestData = {
          username: this.modalUsername,
          pin: this.modalPin
        }

        // Add event_code only for joining existing events
        if (this.modalMode === 'join') {
          requestData.event_code = this.modalEventCode
        }

        const response = await axios.post('/api/events/join-or-create', requestData)

        if (response.data.success) {
          // Store username in localStorage for navbar
          const authData = {
            display_name: response.data.display_name,
            entered_username: this.modalUsername, // Store the username the user entered
            role: response.data.role,
            event_code: response.data.event_code,
            user_id: response.data.user_id || null
          }
          localStorage.setItem('giftExchangeAuth', JSON.stringify(authData))

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

.form-group,
.username-input-group {
  margin-bottom: var(--spacing-4);
}

/* Reduce space between username and PIN */
.username-input-group {
  margin-bottom: var(--spacing-3);
}

/* Ensure proper spacing between PIN and event code */
.form-group:has(#pin) {
  margin-bottom: var(--spacing-5);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.username-input {
  flex: 1;
  padding-right: var(--spacing-12); /* Make space for the button */
}

.refresh-btn {
  position: absolute;
  right: var(--spacing-2);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-2);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.refresh-btn:hover {
  background-color: var(--color-gray-200);
  transform: rotate(45deg);
}

.refresh-btn:active {
  transform: rotate(90deg) scale(0.95);
}

.refresh-icon {
  font-size: var(--font-size-lg);
  line-height: 1;
}

.profile-preview {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  justify-content: center;
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.preview-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-xl);
  color: var(--color-white);
  border: 2px solid var(--color-white);
  box-shadow: var(--shadow-sm);
}

.avatar-initial {
  line-height: 1;
}

.preview-name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.generated-notice {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-4);
}

.generation-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  margin-bottom: var(--spacing-6);
}

.section-divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-6) 0;
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
