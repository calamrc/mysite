import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import OrganizerView from './views/OrganizerView.vue'
import ParticipantView from './views/ParticipantView.vue'
import { AuthService } from './utils/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/organizer/:eventCode?',
    name: 'organizer',
    component: OrganizerView,
    props: true
  },
  {
    path: '/participant/:eventCode?',
    name: 'participant',
    component: ParticipantView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for role-based authorization
router.beforeEach(async (to, from, next) => {
  // Define protected routes and their required roles
  const protectedRoutes = {
    '/organizer': 'organizer',
    '/participant': 'participant'
  }

  // Check if the route is protected
  const isProtectedRoute = Object.keys(protectedRoutes).some(path =>
    to.path.startsWith(path)
  )

  if (!isProtectedRoute) {
    // Not a protected route, allow navigation
    next()
    return
  }

  try {
    // Check authentication status
    const authResult = await AuthService.checkAuthStatus()

    if (!authResult.authenticated) {
      // Not authenticated, redirect to home
      next('/')
      return
    }

    // Extract event code from route params
    const eventCode = to.params.eventCode?.toString().toUpperCase()

    if (!eventCode) {
      // Missing event code, redirect to home
      next('/')
      return
    }

    // Determine required role based on route
    const requiredRole = to.path.startsWith('/organizer') ? 'organizer' : 'participant'

    // Validate role and event access
    const roleValidation = AuthService.validateRoleForRoute(requiredRole, authResult.user, eventCode)

    if (!roleValidation.valid) {
      if (roleValidation.reason === 'wrong_role') {
        // Wrong role - redirect to correct view
        next(roleValidation.redirectTo)
      } else {
        // Other auth issues - redirect to home
        next('/')
      }
      return
    }

    // Authorization successful
    next()

  } catch (error) {
    console.error('Navigation guard error:', error)
    // On error, redirect to home
    next('/')
  }
})

export default router
