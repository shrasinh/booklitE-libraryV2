<script setup>
  import { onMounted, watch } from 'vue'
  import { RouterLink, RouterView } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { login, register, logout } from './components/access.js'
  import Modal from './components/Modal.vue'
  import Alert from './components/Alert.vue'
  import Spinner from './components/Spinner.vue'
  import Theme from './components/Theme.vue'
  import Search from './components/Search.vue'
  import { fetchfunct, checkerror } from './components/fetch.js'
  import { useModalStore, useIdentityStore, useAlertStore, useSearchStore, useLoadingStore } from './stores/store.js'
  import router from './router/index.js'
  import Install from './components/Install.vue'

  const { identity } = storeToRefs( useIdentityStore() )
  const { book_ids, sections } = storeToRefs( useSearchStore() )

  onMounted( () =>
  {
    if ( localStorage.getItem( "Authentication-Token" ) )
    {
      identity.value = JSON.parse( localStorage.getItem( "Identity" ) ) || [ 'Unauthenticated' ]
    }
  } )

  watch( identity, () =>
  {
    const root = document.documentElement
    if ( identity.value.includes( 'User' ) )
      root.style.setProperty( '--navbar-bg', '#248afd' )
    else if ( identity.value.includes( 'Admin' ) )
      root.style.setProperty( '--navbar-bg', '#1a55e3' )
    else
      root.style.setProperty( '--navbar-bg', '#5e6eed' )
  } )

  async function random ()
  {
    if ( book_ids.value.length == 0 )
    {
      useLoadingStore().loading = true
      let r = await fetchfunct( backurl )
      if ( r.ok )
      {
        r = await r.json()
        sections.value = r.sections
        book_ids.value = r.book_ids
      }
      else
      {
        checkerror( r )
      }
      // stopping the loading screen
      useLoadingStore().loading = false
    }
    if ( book_ids.value.length == 0 )
    {
      useAlertStore().alertpush( [ { msg: 'No books are present in the library yet!', type: 'alert-danger' } ] )
    }
    else
    {
      const id = book_ids.value[ Math.floor( Math.random() * book_ids.value.length ) ]
      router.push( `/book/${ id }` )
    }

  }

</script>

<template>

  <nav class="navbar sticky-top navbar-expand-lg">
    <div class="container-fluid">

      <RouterLink class="navbar-brand" to="/">
        <i class="bi bi-book"></i> BookLit
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#Navbar">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="offcanvas offcanvas-end" tabindex="-1" id="Navbar">

        <div class="offcanvas-header">
          <h5 class="offcanvas-title" data-bs-dismiss="offcanvas">
            <RouterLink to="/" class="navbar-brand">
              <i class="bi bi-book"></i> BookLit
            </RouterLink>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>

        <div class="offcanvas-body">
          <ul class="navbar-nav me-auto">

            <li v-if="identity.includes('Admin')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/admin/dashboard">Dashboard</RouterLink>
            </li>
            <li v-if="identity.includes('Admin')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/admin/sections">Sections</RouterLink>
            </li>
            <li v-if="identity.includes('Admin')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/admin/books">Books</RouterLink>
            </li>
            <li v-if="identity.includes('Admin')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/admin/users">Users</RouterLink>
            </li>

            <li v-if="identity.includes('User')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/user/dashboard">Dashboard</RouterLink>
            </li>
            <li v-if="identity.includes('User')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/user/issue">Issued Books</RouterLink>
            </li>
            <li v-if="identity.includes('User')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/user/purchase">Purchased Books</RouterLink>
            </li>
            <li v-if="identity.includes('User')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/user/rating">Ratings</RouterLink>
            </li>

            <li v-if="!identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="useModalStore().modalfunc(logout)">
                <i class="bi bi-box-arrow-right"></i>Logout
              </a>
            </li>
            <li v-if="identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="useModalStore().modalfunc(login)">Login</a>
            </li>
            <li v-if="identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="useModalStore().modalfunc(register)">Register</a>
            </li>
          </ul>

          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <button class="search-button" data-bs-toggle="modal" data-bs-target="#searchModal">
                <i class="bi bi-search"></i> Search
              </button>
            </li>
            <li class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/policies">Policies</RouterLink>
            </li>
            <li class="nav-item" title="pick a random book" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link icon-link icon-link-hover" @click="random">
                <i class="bi bi-shuffle"></i>
              </a>
            </li>
            <li class="nav-item">
              <Theme></Theme>
            </li>
          </ul>

        </div>
      </div>
    </div>
  </nav>
  <Install></Install>
  <Modal></Modal>
  <Search></Search>
  <div v-for="(value,key) in useAlertStore().alerts" :key="key">
    <Alert :alert="value" :id="key"></Alert>
  </div>
  <Spinner></Spinner>

  <RouterView />
</template>

<style scoped>
  .navbar {
    background-color: var(--navbar-bg);
  }

  .navbar-brand i {
    position: relative;
    top: 0;
    transition: top ease 0.5s;
  }

  .navbar-brand:hover i {
    top: -5px;
  }

  .router-link-exact-active.nav-link {
    color: var(--bs-navbar-active-color);
  }

  .router-link-exact-active.nav-link:hover {
    color: var(--bs-navbar-active-color);
  }

  .search-button {
    background: rgba(0, 0, 0, 0.1);
    height: 38px;
    border: 1px solid rgba(132, 124, 124, 0.4);
    border-radius: .375rem
  }

  .search-button:hover {
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(109, 1, 125, 0.499) !important
  }
</style>