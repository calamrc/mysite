<template>
  <div class="participant">
    <!-- Welcome Message -->
    <div class="welcome-message">
      <h1>Welcome, {{ participantName }}!</h1>
    </div>

    <!-- Main Participant Interface -->
    <div class="main-content">
      <div v-if="eventData.phase === 'registration'" class="waiting-state">
        <div class="waiting-icon">⏳</div>
        <h2>Registration Open</h2>
        <p>Waiting for organizer to start the drawing phase...</p>
      </div>

      <div v-else-if="eventData.phase === 'drawing'" class="drawing-section">
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
          <p class="draw-note">This action cannot be undone!</p>
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
import { AuthService } from '@/utils/auth'

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
  async mounted() {
    // First check authentication and role validation
    try {
      const authResult = await AuthService.checkAuthStatus()

      if (!authResult.authenticated) {
        // Not authenticated - redirect to home
        this.$router.push('/')
        return
      }

      // Validate role for participant view
      const roleValidation = AuthService.validateRoleForRoute('participant', authResult.user, this.eventCode)

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
      await this.loadEventData()

    } catch (error) {
      console.error('Authentication check failed:', error)
      // On auth check failure, redirect to home
      this.$router.push('/')
    }
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
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-4) var(--spacing-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-6);
}

.welcome-message {
  text-align: center;
}

.welcome-message h1 {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-4);
}

.main-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
}

.waiting-state,
.drawn-state,
.draw-state {
  text-align: center;
  padding: var(--spacing-8);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
}

.waiting-state {
  background: var(--color-warning-light);
  color: var(--color-warning-dark);
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

.drawing-section {
  width: 100%;
}

.drawn-state {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.success-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-4);
}

.drawn-state h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.drawn-state p {
  font-size: var(--font-size-lg);
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

.draw-state {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.draw-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-4);
}

.draw-state h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.draw-state p {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-6);
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
  .participant {
    padding: var(--spacing-2) var(--spacing-2);
    gap: var(--spacing-4);
  }

  .welcome-message h1 {
    font-size: var(--font-size-3xl);
  }

  .waiting-state,
  .drawn-state,
  .draw-state {
    padding: var(--spacing-6);
  }

  .waiting-icon,
  .success-icon,
  .draw-icon {
    font-size: 3rem;
  }

  .drawn-state h2,
  .draw-state h2,
  .waiting-state h2 {
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
