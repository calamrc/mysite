import axios from 'axios'

export class AuthService {
  /**
   * Check current authentication status and get user data
   * @returns {Promise<{authenticated: boolean, user: object|null, error: string|null}>}
   */
  static async checkAuthStatus() {
    try {
      const response = await axios.get('/api/auth/status', { withCredentials: true })

      if (response.data.authenticated && response.data.user) {
        return {
          authenticated: true,
          user: response.data.user,
          error: null
        }
      } else {
        return {
          authenticated: false,
          user: null,
          error: null
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      return {
        authenticated: false,
        user: null,
        error: error.message
      }
    }
  }

  /**
   * Validate if user has required role for a specific route
   * @param {string} requiredRole - The role required ('organizer' or 'participant')
   * @param {object} user - User object from auth check
   * @param {string} eventCode - Event code from route params
   * @returns {object} Validation result with flags and redirect URL if needed
   */
  static validateRoleForRoute(requiredRole, user, eventCode) {
    if (!user) {
      return {
        valid: false,
        reason: 'not_authenticated',
        redirectTo: '/'
      }
    }

    if (user.event_code !== eventCode) {
      return {
        valid: false,
        reason: 'wrong_event',
        redirectTo: '/'
      }
    }

    if (user.role !== requiredRole) {
      // Wrong role - redirect to correct view
      const correctUrl = user.role === 'organizer'
        ? `/organizer/${user.event_code}`
        : `/participant/${user.event_code}`

      return {
        valid: false,
        reason: 'wrong_role',
        redirectTo: correctUrl
      }
    }

    return {
      valid: true,
      reason: null,
      redirectTo: null
    }
  }

  /**
   * Redirect user to appropriate route based on their role and current event
   * @param {object} user - User object from auth check
   * @param {object} router - Vue router instance
   */
  static redirectToCorrectView(user, router) {
    if (!user || !user.event_code) {
      router.push('/')
      return
    }

    const correctUrl = user.role === 'organizer'
      ? `/organizer/${user.event_code}`
      : `/participant/${user.event_code}`

    router.push(correctUrl)
  }

  /**
   * Check if user is authorized for organizer view
   * @param {object} user - User object from auth check
   * @param {string} eventCode - Event code from route params
   * @returns {boolean} True if user can access organizer view
   */
  static canAccessOrganizerView(user, eventCode) {
    if (!user) return false
    return user.role === 'organizer' && user.event_code === eventCode
  }

  /**
   * Check if user is authorized for participant view
   * @param {object} user - User object from auth check
   * @param {string} eventCode - Event code from route params
   * @returns {boolean} True if user can access participant view
   */
  static canAccessParticipantView(user, eventCode) {
    if (!user) return false
    return user.role === 'participant' && user.event_code === eventCode
  }
}
