import { createRouter, createWebHistory } from 'vue-router'
import Index from './Index.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index,
      meta: {
        title: 'BookLit | A Place of Books and Literature',
      }
    },
    {
      path: '/policies',
      name: 'policies',
      component: () => import('./Policies.vue'),
      meta: {
        title: 'Library Policies',
      }
    },

  ]
})

router.beforeEach((to) => {
  document.title = to.meta.title || 'BookLit'
})

export default router
