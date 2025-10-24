<template>
  <div class="organizer">
    <!-- Main Organizer Interface -->
    <div class="main-content">
      <div class="drawing-section">
        <!-- Registration State -->
        <div v-if="eventData.phase === 'registration'" class="waiting-state">
          <div class="waiting-icon">⏳</div>
          <h2>Registration Open</h2>
          <p>Share the event code <span class='clickable-code' @click='copyEventCode'>{{ codeCopied ? 'Copied!' : eventCode }}</span> to invite participants.</p>
        </div>

        <!-- Participant Drawing States -->
        <div v-else-if="eventData.phase === 'drawing'">
          <div v-if="hasDrawn" class="drawn-state">
            <div class="success-icon">🎁</div>
            <h2>Gift Assignment Complete!</h2>
            <p>You have been assigned to buy a gift for:</p>
            <div class="giftee-name">{{ yourGiftee }}</div>
            <p class="success-note">Happy gifting!</p>
          </div>

          <div v-else class="draw-state">
            <div class="draw-icon">🎯</div>
            <h2>Ready to Draw!</h2>
            <p>It's time to discover who you'll be buying a gift for.</p>
            <button
              @click="makeDraw"
              class="btn btn-success btn-large"
              :disabled="drawing"
            >
              {{ drawing ? 'Drawing...' : 'Make Your Draw' }}
            </button>
          </div>
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

      <!-- Participant Error Messages -->
      <div v-if="drawError" class="error-message">
        <p>{{ drawError }}</p>
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
      isParticipant: true, // Organizers are always participants
      participantName: '', // Organizer's participant name
      loggingOut: false,
      // Participant interface data
      drawing: false,
      drawError: '',
      hasDrawn: false,
      yourGiftee: ''
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

          // Set organizer's participant name from API response
          if (response.data.participant_name) {
            this.participantName = response.data.participant_name
          }

          // Organizers are always participants by default - find this organizer in participants list
          if (this.participantName && this.eventData.participants?.length > 0) {
            const organizer = this.eventData.participants?.find(p =>
              p.name.toLowerCase() === this.participantName.toLowerCase()
            )
            if (organizer) {
              this.hasDrawn = organizer.status.toLowerCase() === 'drawn'
              this.yourGiftee = organizer.giftee_name || ''
            }
          }
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
      navigator.clipboard.writeText(this.eventCode).then(() => {
        this.codeCopied = true
        setTimeout(() => {
          this.codeCopied = false
        }, 2000)
      }).catch(err => {
        console.error('Failed to copy: ', err)
      })
    },

    async makeDraw() {
      if (this.drawing || this.hasDrawn) return

      this.drawing = true
      this.drawError = ''

      try {
        const response = await axios.post(`/api/events/${this.eventCode}/draw`)

        if (response.data.success) {
          this.yourGiftee = response.data.giftee_name
          this.hasDrawn = true
          this.eventData.is_complete = response.data.is_complete
          this.eventData.drawn_count = (this.eventData.drawn_count || 0) + 1
        } else {
          this.drawError = response.data.error || 'Failed to make draw'
        }
      } catch (error) {
        this.drawError = error.response?.data?.error || 'Failed to make draw'
        console.error('Draw error:', error)
      } finally {
        this.drawing = false
        await this.loadEventData() // Refresh data to update participant list
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
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-4) var(--spacing-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-6);
}



.waiting-state,
.drawn-state,
.draw-state {
  text-align: center;
  padding: var(--spacing-8);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  /* Debug borders to verify equal widths */
  border: 2px solid red; /* Remove after confirming equal widths */
}

.waiting-state {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.drawn-state {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.draw-state {
  background: var(--color-accent-light);
  color: var(--color-primary-dark);
}

.waiting-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-4);
}

.waiting-state h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.waiting-state p {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.clickable-code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-weight: var(--font-weight-bold);
  background: rgba(255, 255, 255, 0.8);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  border: 2px solid var(--color-border);
  letter-spacing: 0.025em;
  user-select: none;
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
  width: 100%;
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
  width: 100%;
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
  width: 100%;
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
  width: 100%;
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

.drawing-section {
  width: 100%;
}



.success-icon,
.draw-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-4);
}

.drawn-state h2,
.draw-state h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.drawn-state p,
.draw-state p {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-6);
}

.drawn-state p {
  margin-bottom: var(--spacing-4);
}

.giftee-name {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: rgba(255, 255, 255, 0.8);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  border: 2px solid rgba(255, 255, 255, 0.5);
  margin: var(--spacing-4) 0;
}

.success-note {
  font-size: var(--font-size-base);
  opacity: 0.9;
}

.btn-large {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-4);
}

.draw-note {
  font-size: var(--font-size-base);
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}

.error-message {
  background: var(--color-error-light);
  color: var(--color-error-dark);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-error);
  text-align: center;
  width: 100%;
}

@media (max-width: 768px) {
  .organizer {
    padding: var(--spacing-2) var(--spacing-2);
    gap: var(--spacing-4);
  }

  .waiting-icon {
    font-size: 3rem;
  }

  .waiting-state h2 {
    font-size: var(--font-size-xl);
  }

  .clickable-code {
    padding: var(--spacing-1) var(--spacing-2);
    font-size: var(--font-size-sm);
  }

  .modal-actions {
    flex-direction: column;
  }

  .participants-grid {
    grid-template-columns: 1fr;
  }

  .drawn-state,
  .draw-state {
    padding: var(--spacing-6);
  }

  .success-icon,
  .draw-icon {
    font-size: 3rem;
  }

  .drawn-state h2,
  .draw-state h2 {
    font-size: var(--font-size-xl);
  }

  .giftee-name {
    font-size: var(--font-size-2xl);
    padding: var(--spacing-3);
  }

  .btn-large {
    padding: var(--spacing-3) var(--spacing-6);
    font-size: var(--font-size-lg);
  }
}
</style>
