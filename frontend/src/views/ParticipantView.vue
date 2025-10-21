<template>
  <div class="participant">
  <div class="header">
    <div class="title-section">
        <h1>Gift Exchange</h1>
        <div class="event-code-display">
          <span class="label">Event:</span>
          <span class="code">{{ eventCode }}</span>
        </div>
      </div>
      <button @click="logout" class="btn btn-secondary" :disabled="loggingOut">
        {{ loggingOut ? 'Logging Out...' : '🚪 Logout' }}
      </button>
    </div>

    <!-- Main Participant Interface -->
    <div class="main-content">
      <!-- Status Overview -->
      <div class="status-overview">
        <div class="status-card">
          <h3>📊 Your Status</h3>
          <div class="status-info">
            <div class="welcome-message">
              <h4>Welcome, {{ participantName }}! 🎉</h4>
              <p>{{ getPhaseDescription() }}</p>
            </div>

            <div v-if="eventData.phase === 'registration'" class="waiting-card">
              <div class="waiting-icon">⏳</div>
              <h4>Registration Open</h4>
              <p>Waiting for organizer to start the drawing phase...</p>
              <div class="participant-count">
                <span class="count">{{ eventData.joined_count || 0 }}</span>
                <span class="label">participants joined</span>
              </div>
            </div>

            <div v-else-if="eventData.phase === 'drawing'" class="drawing-section">
              <div v-if="hasDrawn" class="drawn-card">
                <div class="success-icon">🎁</div>
                <h4>Gift Assignment Complete!</h4>
                <p>You have been assigned to buy a gift for:</p>
                <div class="giftee-name">{{ yourGiftee }}</div>
                <p>Happy gifting! 🎄</p>
              </div>

              <div v-else class="draw-card">
                <div class="draw-icon">🎯</div>
                <h4>Ready to Draw!</h4>
                <p>It's time to discover who you'll be buying a gift for.</p>
                <button
                  @click="makeDraw"
                  class="btn btn-success btn-large"
                  :disabled="drawing"
                >
                  {{ drawing ? 'Drawing...' : '🎁 Make Your Draw' }}
                </button>
                <p class="draw-note">✨ This action cannot be undone!</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Event Progress -->
      <div class="progress-section">
        <div class="progress-card">
          <h3>📈 Event Progress</h3>
          <div class="progress-stats">
            <div class="stat">
              <span class="number">{{ eventData.joined_count || 0 }}</span>
              <span class="label">Total Participants</span>
            </div>
            <div class="stat">
              <span class="number">{{ eventData.drawn_count || 0 }}</span>
              <span class="label">Have Drawn</span>
            </div>
          </div>

          <div v-if="eventData.is_complete && !hasDrawn" class="waiting-notice">
            <p><strong>Event Complete!</strong> All participants have made their draws.</p>
            <p>You may still make your draw if you haven't already.</p>
          </div>
        </div>
      </div>

      <!-- Rules & Tips -->
      <div class="rules-section">
        <div class="rules-card">
          <h3>📋 Gift Exchange Rules</h3>
          <ul class="rules-list">
            <li>You will be randomly assigned to buy a gift for one person</li>
            <li>You cannot draw yourself or someone who has already been assigned</li>
            <li>Keep your assignment secret until the exchange!</li>
            <li>The drawing is final once you make your selection</li>
          </ul>
        </div>
      </div>

      <!-- Error Messages -->
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ParticipantView',
  props: {
    eventCode: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      participantName: '',
      eventData: {
        phase: 'registration',
        joined_count: 0,
        drawn_count: 0,
        is_complete: false,
        participants: []
      },
      drawing: false,
      loading: false,
      drawError: '',
      error: '',
      hasDrawn: false,
      yourGiftee: '',
      loggingOut: false
    }
  },
  mounted() {
    this.loadEventData()
  },
  methods: {
    async loadEventData() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get(`/api/events/${this.eventCode}/status`)

        if (response.data.success) {
          this.eventData = response.data

          // Set participant name from API response
          if (response.data.participant_name) {
            this.participantName = response.data.participant_name
          }

          // Check if this participant has already drawn
          if (this.participantName) {
            const participant = this.eventData.participants?.find(p =>
              p.name.toLowerCase() === this.participantName.toLowerCase()
            )
            if (participant) {
              this.hasDrawn = participant.status.toLowerCase() === 'drawn'
              this.yourGiftee = participant.giftee_name || ''
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

    async makeDraw() {
      if (this.drawing || this.hasDrawn) return

      if (!confirm('Are you ready to discover your gift assignment? This cannot be undone!')) {
        return
      }

      this.drawing = true
      this.drawError = ''

      try {
        const response = await axios.post(`/api/events/${this.eventCode}/draw`)

        if (response.data.success) {
          this.yourGiftee = response.data.giftee_name
          this.hasDrawn = true
          this.eventData.is_complete = response.data.is_complete
          this.eventData.drawn_count = (this.eventData.drawn_count || 0) + 1

          // Success message could be shown here
          alert(`🎁 You have been assigned to buy a gift for: ${this.yourGiftee}\n\nHappy gifting! 🎄`)
        } else {
          this.drawError = response.data.error || 'Failed to make draw'
        }
      } catch (error) {
        this.drawError = error.response?.data?.error || 'Failed to make draw'
        console.error('Draw error:', error)
      } finally {
        this.drawing = false
      }
    },

    getPhaseDescription() {
      if (this.eventData.phase === 'registration') {
        return 'The event is currently accepting participants. You\'ll be able to make your draw once the organizer starts the drawing phase.'
      } else if (this.eventData.phase === 'drawing') {
        if (this.hasDrawn) {
          return 'You have successfully made your gift assignment!'
        } else {
          return 'It\'s time to discover your gift assignment. Click the button below to make your draw!'
        }
      }
      return 'Loading event status...'
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
.participant {
  max-width: 800px;
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



.status-overview {
  margin-bottom: 2rem;
}

.status-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.status-card h3 {
  margin-bottom: 2rem;
  color: #2c3e50;
  text-align: center;
}

.welcome-message {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.welcome-message h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.welcome-message p {
  color: #666;
}

.waiting-card {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
}

.waiting-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.waiting-card h4 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.participant-count {
  margin-top: 1rem;
  padding: 0.5rem;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: inline-block;
}

.participant-count .count {
  font-size: 1.5rem;
  font-weight: bold;
  display: block;
}

.participant-count .label {
  font-size: 0.9rem;
}

.drawing-section {
  margin-top: 2rem;
}

.drawn-card {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.drawn-card h4 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.giftee-name {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 1rem 0;
  padding: 1rem;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  border: 2px solid rgba(255,255,255,0.3);
}

.draw-card {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
}

.draw-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.draw-card h4 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.btn-large {
  padding: 1rem 3rem;
  font-size: 1.2rem;
  margin: 1rem 0;
}

.btn-success {
  background-color: #f39c12;
  border: none;
}

.btn-success:hover:not(:disabled) {
  background-color: #e67e22;
}

.draw-note {
  font-size: 0.9rem;
  margin-top: 1rem;
  opacity: 0.9;
}

.progress-section {
  margin-bottom: 2rem;
}

.progress-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.progress-card h3 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  text-align: center;
}

.progress-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-bottom: 1.5rem;
}

.stat {
  text-align: center;
}

.stat .number {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
}

.stat .label {
  color: #666;
  font-size: 1rem;
}

.waiting-notice {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #3498db;
}

.waiting-notice strong {
  color: #2c3e50;
}

.rules-section {
  margin-bottom: 2rem;
}

.rules-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.rules-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.rules-list {
  list-style: none;
  padding: 0;
}

.rules-list li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
}

.rules-list li:last-child {
  border-bottom: none;
}

.rules-list li:before {
  content: '🎄';
  position: absolute;
  left: 0;
  top: 0.5rem;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
  text-align: center;
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

  .progress-stats {
    flex-direction: column;
    gap: 1.5rem;
    align-items: center;
  }

  .modal-actions {
    flex-direction: column;
  }

  .waiting-card,
  .drawn-card,
  .draw-card {
    padding: 1.5rem;
  }

  .giftee-name {
    font-size: 1.5rem;
  }
}
</style>
