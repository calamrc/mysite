<template>
  <div class="user-avatar-container">
    <!-- Avatar Button -->
    <button
      @click.stop="toggleMenu"
      class="avatar-btn"
      :aria-expanded="isOpen"
      :aria-label="'User menu for ' + currentUser.display_name"
      type="button"
    >
      <div class="avatar-circle">
        <span class="avatar-initial">{{ userInitial }}</span>
      </div>
    </button>

    <!-- Dropdown Menu -->
    <div v-if="isOpen" class="avatar-dropdown-menu" @click.stop>
      <button @click="logout" class="menu-item btn btn-outline" :disabled="loggingOut">
        <span v-if="loggingOut" class="loading-spinner" aria-hidden="true"></span>
        {{ loggingOut ? 'Logging Out...' : 'Logout' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserAvatar',
  props: {
    currentUser: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isOpen: false,
      loggingOut: false
    }
  },
  computed: {
    userInitial() {
      if (this.currentUser && this.currentUser.username) {
        return this.currentUser.username.charAt(0).toUpperCase()
      }
      return '?'
    }
  },
  mounted() {
    // Close menu when clicking outside
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
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
.user-avatar-container {
  position: relative;
}

.avatar-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-1);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
  display: flex;
  align-items: center;
}

.avatar-btn:hover {
  background-color: var(--color-gray-100);
}

.avatar-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-white);
  box-shadow: var(--shadow-sm);
}

.avatar-initial {
  color: var(--color-white);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Dropdown Menu */
.avatar-dropdown-menu {
  position: absolute;
  top: calc(100% + var(--spacing-2));
  right: 0;
  background-color: var(--color-surface);
  min-width: 200px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2);
  z-index: 1000;
}

.menu-item {
  width: 100%;
  justify-content: flex-start;
  margin-bottom: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-4);
}

.menu-item:last-child {
  margin-bottom: 0;
}

.menu-item:hover:not(:disabled) {
  background-color: var(--color-gray-50);
}

@media (max-width: 768px) {
  .avatar-circle {
    width: 36px;
    height: 36px;
  }

  .avatar-initial {
    font-size: var(--font-size-base);
  }

  .avatar-dropdown-menu {
    min-width: 180px;
    right: var(--spacing-2);
  }
}
</style>
