<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- User Name (Left side) -->
      <div v-if="currentUser" class="user-name-display">
        {{ currentUser.display_name }}
      </div>

      <!-- Brand Name -->
      <router-link v-else to="/" class="navbar-brand" aria-label="Gift Exchange Manager Home">
        <span class="brand-text">Gift Exchange Manager</span>
      </router-link>

      <!-- Hamburger Menu Button -->
      <button
        class="hamburger-btn"
        @click="toggleMenu"
        :aria-expanded="isOpen"
        aria-label="Toggle navigation menu"
      >
        <span class="hamburger-line" :class="{ 'is-open': isOpen }"></span>
        <span class="hamburger-line" :class="{ 'is-open': isOpen }"></span>
        <span class="hamburger-line" :class="{ 'is-open': isOpen }"></span>
      </button>
    </div>

    <!-- Mobile Menu Overlay -->
    <div v-if="isOpen" class="mobile-menu-overlay" @click="closeMenu">
      <div class="mobile-menu" @click.stop>
        <button @click="logout" class="menu-item btn btn-outline" :disabled="loggingOut">
          <span v-if="loggingOut" class="loading-spinner" aria-hidden="true"></span>
          {{ loggingOut ? 'Logging Out...' : 'Logout' }}
        </button>
      </div>
    </div>


  </nav>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Navbar',
  data() {
    return {
      isOpen: false,
      loggingOut: false
    }
  },
  computed: {
    currentUser() {
      // Get current user from localStorage
      try {
        const authData = localStorage.getItem('giftExchangeAuth')
        if (authData) {
          const parsed = JSON.parse(authData)
          return {
            display_name: parsed.display_name
          }
        }
      } catch (e) {
        console.error('Error reading auth data:', e)
      }
      return null
    }
  },
  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen
    },

    closeMenu() {
      this.isOpen = false
    },

    async logout() {
      if (this.loggingOut) return

      this.loggingOut = true
      this.closeMenu()

      try {
        await axios.post('/api/logout')
        localStorage.removeItem('giftExchangeAuth')
        this.$router.push('/')
      } catch (error) {
        console.error('Logout error:', error)
        this.$router.push('/')
      } finally {
        this.loggingOut = false
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

.hamburger-btn {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 30px;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-1);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.hamburger-btn:hover {
  background-color: var(--color-gray-100);
}

.hamburger-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.hamburger-line {
  width: 100%;
  height: 3px;
  background-color: var(--color-text-primary);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger-line:nth-child(1).is-open {
  transform: rotate(45deg) translate(6px, 6px);
}

.hamburger-line:nth-child(2).is-open {
  opacity: 0;
}

.hamburger-line:nth-child(3).is-open {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* Mobile Menu */
.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding-top: var(--spacing-16);
}

.mobile-menu {
  background-color: var(--color-surface);
  min-width: 250px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-right: var(--spacing-4);
  padding: var(--spacing-2);
}

.menu-item {
  width: 100%;
  justify-content: flex-start;
  margin-bottom: var(--spacing-2);
}

.menu-item:last-child {
  margin-bottom: 0;
}

/* User Name Display */
.user-name-display {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
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
