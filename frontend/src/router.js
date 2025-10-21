import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import OrganizerView from './views/OrganizerView.vue'
import ParticipantView from './views/ParticipantView.vue'

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

export default router
