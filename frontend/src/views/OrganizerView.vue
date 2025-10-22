<template>
  <div class="organizer">
    <!-- Event Status Badge -->
    <div class="status-badge" :class="eventData.phase">
      {{ getPhaseDisplay() }}
    </div>

    <!-- Event Code Section -->
    <div class="event-code-section">
      <div class="event-code-display">
        <span class="code">{{ eventCode }}</span>
        <button @click="copyEventCode" class="btn btn-sm" :disabled="codeCopied" aria-label="Copy event code">
          <span v-if="codeCopied" aria-hidden="true">✅</span>
          <span v-else aria-hidden="true">📋</span>
          {{ codeCopied ? 'Copied!' : 'Copy' }}
        </button>
      </div>
    </div>

    <!-- Main Organizer Interface -->
    <div class="main-content">

      <!-- Join as Participant -->
      <div v-if="eventData.phase === 'registration' && !isParticipant" class="join-participant-section">
        <div class="control-card">
          <h3>Join as Participant</h3>
          <p>As the organizer, you can also participate in the gift exchange. Enter your name to join.</p>

          <form @submit.prevent="joinAsParticipant" class="participant-form">
            <div class="form-group">
              <label for="participant-name" class="visually-hidden">Your Name</label>
              <input
                id="participant-name"
                v-model="participantName"
                type="text"
                placeholder="Enter your name"
                maxlength="50"
                class="form-control"
                required
              />
            </div>
            <button type="submit" class="btn btn-primary" :disabled="joiningAsParticipant">
              <span v-if="joiningAsParticipant" class="loading-spinner" aria-hidden="true"></span>
              {{ joiningAsParticipant ? 'Joining...' : 'Join Exchange' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Phase-specific controls -->
      <div v-if="eventData.phase === 'registration'" class="phase-controls">
        <div class="control-card">
          <h3>Start Drawing Phase</h3>
          <p>Once participants have joined, start the drawing phase to begin gift assignments.</p>
          <button
            @click="startDrawingPhase"
            class="btn btn-success"
            :disabled="startingPhase || (eventData.joined_count || 0) < 2"
          >
            {{ startingPhase ? 'Starting...' : 'Start Drawing Phase' }}
          </button>
          <p v-if="(eventData.joined_count || 0) < 2" class="warning">
            Need at least 2 participants to start drawing
          </p>
        </div>
      </div>

      <!-- Participants List -->
      <div class="participants-section">
        <h3>Participants ({{ eventData.participants?.length || 0 }})</h3>

        <div v-if="eventData.participants?.length === 0" class="empty-state">
          <p>No participants have joined yet. Share the event code <strong>{{ eventCode }}</strong> with others!</p>
        </div>

        <div v-else class="participants-grid">
          <div
            v-for="participant in eventData.participants"
            :key="participant.id"
            class="participant-card"
          >
            <div class="participant-info">
              <h4>{{ participant.name }}</h4>
              <div class="participant-status">
                <span class="status-badge" :class="participant.status.toLowerCase()">
                  {{ participant.status }}
                </span>
                <small v-if="participant.giftee_name">→ {{ participant.giftee_name }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Event Complete Message -->
      <div v-if="eventData.is_complete" class="completion-message">
        <div class="completion-card">
          <h3>Exchange Complete!</h3>
          <p>All participants have made their draws. The gift exchange is now ready to begin!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { AuthService } from '@/utils/auth'

export default {
  name: 'OrganizerView',
  props: {
    eventCode: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isAuthenticated: false,
      eventData: {
        phase: 'loading',
        participants: [],
        joined_count: 0,
        drawn_count: 0,
        is_complete: false,
        user_role: 'organizer'
      },
      startingPhase: false,
      codeCopied: false,
      loading: false,
      error: '',
      participantName: '',
      joiningAsParticipant: false,
      isParticipant: false,
      loggingOut: false
    }
  },
  mounted() {
    // Try to authenticate if we have an event code
    if (this.eventCode) {
      this.checkAuthentication()
    }
  },
  methods: {
    async checkAuthentication() {
      try {
        // Check authentication status and role
        const authResult = await AuthService.checkAuthStatus()

        if (!authResult.authenticated) {
          // Not authenticated - redirect to home
          this.$router.push('/')
          return
        }

        // Validate role for organizer view
        const roleValidation = AuthService.validateRoleForRoute('organizer', authResult.user, this.eventCode)

        if (!roleValidation.valid) {
          if (roleValidation.reason === 'wrong_role') {
            // Wrong role - redirect to correct view
            this.$router.push(roleValidation.redirectTo)
          } else {
            // Other auth issues - redirect to home
            this.$router.push('/')
          }
          return
        }

        // User is authorized - load event data
        this.isAuthenticated = true
        await this.loadEventData()

      } catch (error) {
        console.error('Authentication check failed:', error)
        // On auth check failure, redirect to home
        this.$router.push('/')
      }
    },



    async loadEventData() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get(`/api/events/${this.eventCode}/status`)

        if (response.data.success) {
          this.eventData = response.data
          // Set isParticipant based on API response
          this.isParticipant = response.data.is_participant || false
        } else {
          this.error = response.data.error || 'Failed to load event data'
        }
      } catch (error) {
        this.error = 'Error loading event data: ' + error.message
        console.error('Load error:', error)
      } finally {
        this.loading = false
      }
    },

    async startDrawingPhase() {
      if (this.startingPhase) return

      this.startingPhase = true
      this.error = ''

      try {
        const response = await axios.post(`/api/events/${this.eventCode}/start-drawing`)

        if (response.data.success) {
          await this.loadEventData() // Refresh data
        } else {
          this.error = response.data.error || 'Failed to start drawing phase'
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to start drawing phase'
        console.error('Start phase error:', error)
      } finally {
        this.startingPhase = false
      }
    },

    copyEventCode() {
      navigator.clipboard.writeText(this.eventCode.toUpperCase()).then(() => {
        this.codeCopied = true
        setTimeout(() => {
          this.codeCopied = false
        }, 2000)
      }).catch(err => {
        console.error('Failed to copy: ', err)
      })
    },

    getPhaseDisplay() {
      const phaseMap = {
        'registration': 'Registration Open',
        'drawing': 'Drawing Phase'
      }
      return phaseMap[this.eventData.phase] || this.eventData.phase
    },

    async joinAsParticipant() {
      if (this.joiningAsParticipant) return

      this.joiningAsParticipant = true
      this.error = ''

      try {
        const response = await axios.post(`/api/events/${this.eventCode}/participants`, {
          name: this.participantName.trim()
        })

        if (response.data.success) {
          this.isParticipant = true
          await this.loadEventData() // Refresh to show updated participant list
          this.participantName = '' // Clear the form
        } else {
          this.error = response.data.error || 'Failed to join as participant'
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to join as participant'
        console.error('Join participant error:', error)
      } finally {
        this.joiningAsParticipant = false
      }
    },

    async logout() {
      if (this.loggingOut) return

      this.loggingOut = true

      try {
        await axios.post('/api/logout')
        // Redirect to home page after successful logout
        this.$router.push('/')
      } catch (error) {
        console.error('Logout error:', error)
        // Still redirect to home even if logout API fails
        this.$router.push('/')
      } finally {
        this.loggingOut = false
      }
    }
  }
}
</script>

<style scoped>
.organizer {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-4) var(--spacing-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-8);
}

.status-badge {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--radius-xl);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-lg);
  text-align: center;
}

.status-badge.registration {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.status-badge.drawing {
  background: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.event-code-section {
  text-align: center;
}

.event-code-display {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-4);
  background: var(--color-surface);
  padding: var(--spacing-6);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.event-code-display .code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  background: var(--color-background);
  padding: var(--spacing-3);
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border);
  min-width: 120px;
  text-align: center;
  letter-spacing: 0.025em;
}

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

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.auth-form {
  margin-top: 1rem;
}

.phase-info {
  margin-bottom: 2rem;
}

.phase-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.phase-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.phase-details {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.phase-indicator {
  flex-shrink: 0;
}

.phase-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
}

.phase-indicator.registration .phase-badge {
  background: #3498db;
  color: white;
}

.phase-indicator.drawing .phase-badge {
  background: #e67e22;
  color: white;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.phase-controls {
  margin-bottom: 2rem;
}

.control-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.control-card h3 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.control-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

.btn-success {
  background-color: #27ae60;
}

.btn-success:hover:not(:disabled) {
  background-color: #229954;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.warning {
  color: #e67e22;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.participants-section {
  margin-bottom: 2rem;
}

.participants-section h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  color: #666;
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.participant-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #3498db;
}

.participant-info h4 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.participant-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.joined {
  background: #3498db;
  color: white;
}

.status-badge.drawn {
  background: #27ae60;
  color: white;
}

.participant-status small {
  color: #666;
  font-weight: 500;
}

.completion-message {
  margin-bottom: 2rem;
}

.completion-card {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(39, 174, 96, 0.2);
}

.completion-card h3 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.error {
  color: #e74c3c;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

@media (max-width: 768px) {
  .organizer {
    padding: var(--spacing-2) var(--spacing-2);
    gap: var(--spacing-4);
  }

  .status-badge {
    padding: var(--spacing-2) var(--spacing-4);
    font-size: var(--font-size-base);
  }

  .event-code-display {
    flex-direction: column;
    gap: var(--spacing-3);
    padding: var(--spacing-4);
  }

  .event-code-display .code {
    font-size: var(--font-size-2xl);
    min-width: 100px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .participants-grid {
    grid-template-columns: 1fr;
  }
}
</style>
