import { createRouter, createWebHistory } from 'vue-router'
import { useAlertStore, useIdentityStore } from '../stores/store.js'
import Index from './Index.vue'
import Notfound from './Notfound.vue'

const router = createRouter( {
  history: createWebHistory( import.meta.env.BASE_URL ),
  routes: [
    {
      path: '/',
      component: Index,
      meta: {
        title: 'BookLit | A Place of Books and Literature',
      }
    },
    {
      path: '/policies',
      component: () => import( './Policies.vue' ),
      meta: {
        title: 'Library Policies',
      }
    },
    {
      path: '/admin/dashboard',
      component: () => import( './admin/Dashboard.vue' ),
      meta: {
        title: "Admin Dashboard", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/admin/sections',
      component: () => import( './admin/Sections.vue' ),
      meta: {
        title: "Sections", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/admin/sections/create',
      component: () => import( './admin/Sectioncreate.vue' ),
      meta: {
        title: "Section creation", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/admin/books',
      component: () => import( './admin/Books.vue' ),
      meta: {
        title: "Books", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/admin/books/create',
      component: () => import( './admin/Bookcreate.vue' ),
      meta: {
        title: "Book creation", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/admin/users',
      component: () => import( './admin/Users.vue' ),
      meta: {
        title: "Users", requiresAuth: true, auth_role: "Admin"
      },
    },
    {
      path: '/book/:id',
      component: () => import( './Book.vue' ),
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'Notfound',
      component: Notfound
    },




  ],
  scrollBehavior ( to, from, savedposition )
  {
    if ( savedposition ) return savedposition
    return { x: 0, y: 0 }
  }
} )

router.beforeEach( ( to, from ) =>
{
  document.title = to.meta.title || 'BookLit'

  if ( to.meta.requiresAuth )
  {
    if ( ( to.meta.auth_role == "Admin" && !useIdentityStore().identity.includes( "Admin" ) ) || ( to.meta.auth_role == "User" && !useIdentityStore().identity.includes( "User" ) ) )
    {
      useAlertStore().alertpush( [ { msg: "You don't have sufficient for this action! Please login with the correct account.", type: 'alert-danger' } ] )
      return {
        path: '/'
      }
    }
  }
}
)

export default router
