<template>
  <div class="organizer">
  <div class="header">
    <div class="title-section">
        <h1>🎄 Gift Exchange Organizer</h1>
        <div class="event-code-display">
          <span class="label">Event Code:</span>
          <span class="code">{{ eventCode }}</span>
          <button @click="copyEventCode" class="btn btn-small" :disabled="codeCopied">
            {{ codeCopied ? '✅ Copied!' : '📋 Copy' }}
          </button>
        </div>
      </div>
      <button @click="logout" class="btn btn-secondary" :disabled="loggingOut">
        {{ loggingOut ? 'Logging Out...' : '🚪 Logout' }}
      </button>
    </div>

    <!-- Main Organizer Interface -->
    <div class="main-content">
      <!-- Event Phase Info -->
      <div class="phase-info">
        <div class="phase-card">
          <h3>📊 Event Status</h3>
          <div class="phase-details">
            <div class="phase-indicator" :class="eventData.phase">
              <span class="phase-badge">{{ getPhaseDisplay() }}</span>
            </div>
            <div class="stats">
              <div class="stat-item">
                <span class="stat-number">{{ eventData.joined_count || 0 }}</span>
                <span class="stat-label">Participants</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ eventData.drawn_count || 0 }}</span>
                <span class="stat-label">Drawn</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Join as Participant -->
      <div v-if="eventData.phase === 'registration' && !isParticipant" class="join-participant-section">
        <div class="control-card">
          <h3>🎁 Join as Participant</h3>
          <p>As the organizer, you can also participate in the gift exchange. Enter your name to join.</p>

          <form @submit.prevent="joinAsParticipant" class="participant-form">
            <div class="form-group">
              <input
                v-model="participantName"
                type="text"
                placeholder="Enter your name"
                maxlength="50"
                required
              />
            </div>
            <button type="submit" class="btn btn-primary" :disabled="joiningAsParticipant">
              {{ joiningAsParticipant ? 'Joining...' : 'Join Exchange' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Phase-specific controls -->
      <div v-if="eventData.phase === 'registration'" class="phase-controls">
        <div class="control-card">
          <h3>🎯 Start Drawing Phase</h3>
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
        <h3>👥 Participants ({{ eventData.participants?.length || 0 }})</h3>

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
          <h3>🎉 Exchange Complete!</h3>
          <p>All participants have made their draws. The gift exchange is now ready to begin!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

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
      // Skip authentication modal if user is already authenticated (created the event)
      // Try to load event data directly - if it fails, show auth modal
      try {
        await this.loadEventData()
        // If loadEventData succeeds, user is authenticated
        this.isAuthenticated = true
      } catch (error) {
        // If it fails, stay with modal
        this.isAuthenticated = false
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

      if (!confirm('Are you sure you want to logout? You will need to log back in to access the event.')) {
        return
      }

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
  padding: 0 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.title-section h1 {
  margin-bottom: 0.5rem;
  font-size: 2rem;
  color: #2c3e50;
}

.event-code-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.event-code-display .label {
  font-weight: bold;
  color: #666;
}

.event-code-display .code {
  font-family: monospace;
  font-size: 1.2rem;
  font-weight: bold;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: #2c3e50;
  letter-spacing: 1px;
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
  .header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .phase-details {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .stats {
    gap: 1rem;
  }

  .modal-actions {
    flex-direction: column;
  }

  .participants-grid {
    grid-template-columns: 1fr;
  }
}
</style>
