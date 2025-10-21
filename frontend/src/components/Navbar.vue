<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- User Info (Left side) -->
      <div v-if="currentUser.user && currentUser.user.display_name" class="user-info" @click="openEditModal">
        <div class="user-avatar" :style="{ backgroundColor: currentUser.user.avatar_color }">
          <span class="avatar-initial">{{ currentUser.user.display_name.charAt(0).toUpperCase() }}</span>
        </div>
        <span class="user-name">{{ currentUser.user.display_name }}</span>
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

    <!-- Profile Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <h3>Edit Profile</h3>

        <div class="profile-preview">
          <div class="preview-avatar" :style="{ backgroundColor: editForm.avatar_color }">
            <span class="avatar-initial">{{ editForm.display_name.charAt(0).toUpperCase() }}</span>
          </div>
          <span class="preview-name">{{ editForm.display_name }}</span>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="form-group">
            <label for="edit-display-name">Display Name</label>
            <input
              id="edit-display-name"
              v-model="editForm.display_name"
              type="text"
              maxlength="50"
              class="form-control"
              required
            />
          </div>

          <div class="avatar-options">
            <label>Choose Avatar Color</label>
            <div class="color-grid">
              <button
                v-for="color in avatarColors"
                :key="color"
                type="button"
                :class="{ 'color-selected': editForm.avatar_color === color }"
                :style="{ backgroundColor: color }"
                @click="selectColor(color)"
                class="color-option"
                :aria-label="`Select ${color} avatar color`"
              ></button>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="regenerateProfile" class="btn btn-secondary">
              🔄 Regenerate
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="loading-spinner" aria-hidden="true"></span>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
            <button type="button" @click="closeEditModal" class="btn btn-outline">Cancel</button>
          </div>
        </form>

        <p v-if="editError" class="error">{{ editError }}</p>
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
      loggingOut: false,
      showEditModal: false,
      saving: false,
      editError: '',
      avatarColors: [
        '#ff6b6b', '#feca57', '#48dbfb', '#0abde3', '#ff9ff3', '#f368e0',
        '#00d2d3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43', '#ee5a24',
        '#0abde3', '#2e86de', '#341f97', '#5352ed', '#ff6b9d', '#e056fd',
        '#3483fa', '#26de81', '#78e08f', '#fad390', '#6c5ce7', '#a29bfe',
        '#fd79a8', '#fdcb6e', '#e17055', '#d63031', '#00b894', '#00cec9',
        '#a29bfe', '#6c5ce7'
      ]
    }
  },
  computed: {
    currentUser() {
      // Get current user from session storage or Vuex/state management
      // For now, checking from a global auth state or localStorage
      try {
        const authData = localStorage.getItem('giftExchangeAuth')
        if (authData) {
          const parsed = JSON.parse(authData)
          return {
            authenticated: true,
            user: {
              display_name: parsed.display_name,
              avatar_color: parsed.avatar_color
            }
          }
        }
      } catch (e) {
        console.error('Error reading auth data:', e)
      }
      return { authenticated: false, user: null }
    },
    editForm: {
      get() {
        return {
          display_name: this.currentUser.user?.display_name || '',
          avatar_color: this.currentUser.user?.avatar_color || '#6366f1'
        }
      },
      set(value) {
        // Not used since we use individual fields
      }
    }
  },
  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen
    },

    closeMenu() {
      this.isOpen = false
    },

    openEditModal() {
      this.showEditModal = true
      this.editError = ''
    },

    closeEditModal() {
      this.showEditModal = false
      this.editError = ''
      this.saving = false
    },

    selectColor(color) {
      this.editForm.avatar_color = color
    },

    regenerateProfile() {
      // Generate new random name and color
      const randomNameIndex = Math.floor(Math.random() * 50) // Match backend word count
      const randomColorIndex = Math.floor(Math.random() * this.avatarColors.length)

      this.editForm.display_name = `Temp${randomNameIndex}` // Temporary naming
      this.editForm.avatar_color = this.avatarColors[randomColorIndex]
    },

    async saveProfile() {
      if (this.saving) return

      this.saving = true
      this.editError = ''

      try {
        const response = await axios.put('/api/user/profile', {
          display_name: this.editForm.display_name,
          avatar_color: this.editForm.avatar_color
        })

        if (response.data.success) {
          // Update localStorage
          const currentAuth = JSON.parse(localStorage.getItem('giftExchangeAuth') || '{}')
          currentAuth.display_name = this.editForm.display_name
          currentAuth.avatar_color = this.editForm.avatar_color
          localStorage.setItem('giftExchangeAuth', JSON.stringify(currentAuth))

          // Close modal and emit success
          this.closeEditModal()
          // Could emit event to parent components to refresh
          this.$emit('profile-updated', response.data)
        } else {
          this.editError = response.data.error || 'Failed to update profile'
        }
      } catch (error) {
        this.editError = error.response?.data?.error || 'Failed to update profile'
        console.error('Profile update error:', error)
      } finally {
        this.saving = false
      }
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

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  position: relative;
}

.user-info:hover {
  background-color: var(--color-surface-hover);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
  color: var(--color-white);
  border: 2px solid var(--color-white);
  box-shadow: var(--shadow-sm);
}

.avatar-initial {
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.user-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Profile Edit Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4);
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 400px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  padding: var(--spacing-6);
}

.modal-content h3 {
  margin-bottom: var(--spacing-6);
  color: var(--color-text-primary);
  text-align: center;
}

.profile-preview {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  justify-content: center;
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-surface-hover);
  border-radius: var(--radius-lg);
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
  box-shadow: var(--shadow-md);
}

.preview-name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.avatar-options {
  margin-bottom: var(--spacing-6);
}

.avatar-options label {
  display: block;
  margin-bottom: var(--spacing-3);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: var(--spacing-2);
}

.color-option {
  width: 30px;
  height: 30px;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.color-option:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-sm);
}

.color-option.color-selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
  transform: scale(1.05);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  margin-top: var(--spacing-6);
}

.error {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  text-align: center;
  margin-top: var(--spacing-3);
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
