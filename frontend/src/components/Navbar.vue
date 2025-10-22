<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Brand Name (always visible) -->
      <router-link to="/" class="navbar-brand" aria-label="Gift Exchange Manager Home">
        <span class="brand-text">Gift Exchange Manager</span>
      </router-link>

      <!-- User Avatar Menu Button -->
      <UserAvatar v-if="showAvatar" :current-user="currentUser" />
    </div>
  </nav>
</template>

<script>
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'Navbar',
  components: {
    UserAvatar
  },
  data() {
    return {
      authData: null
    }
  },
  computed: {
    currentUser() {
      if (this.authData) {
        return {
          display_name: this.authData.display_name,
          username: this.authData.entered_username || this.authData.display_name // Use entered username for avatar
        }
      }
      return null
    },
    showAvatar() {
      // Show avatar only when authenticated AND not on home route
      const isAuthenticated = !!this.currentUser
      const isNotHomeRoute = this.$route?.path !== '/'
      return isAuthenticated && isNotHomeRoute
    }
  },
  mounted() {
    // Initialize auth data
    this.loadAuthData()

    // Listen for storage changes (when user logs in/out)
    window.addEventListener('storage', this.handleStorageChange)
  },
  watch: {
    '$route'() {
      // Reload auth data whenever route changes
      this.loadAuthData()
    }
  },
  beforeDestroy() {
    window.removeEventListener('storage', this.handleStorageChange)
  },
  methods: {
    loadAuthData() {
      try {
        const authData = localStorage.getItem('giftExchangeAuth')
        if (authData) {
          this.authData = JSON.parse(authData)
        } else {
          this.authData = null
        }
      } catch (e) {
        console.error('Error reading auth data:', e)
        this.authData = null
      }
    },

    handleStorageChange(event) {
      // Reload auth data when localStorage changes
      if (event.key === 'giftExchangeAuth' || event.key === null) {
        this.loadAuthData()
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-4);
  height: var(--spacing-16);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.navbar-brand:hover {
  color: var(--color-primary-hover);
}

.brand-text {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 var(--spacing-3);
  }

  .navbar-brand {
    font-size: var(--font-size-lg);
  }
}
</style>
