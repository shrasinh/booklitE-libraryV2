<script setup>
import {computed,onMounted} from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import {login, register, logout} from './components/access.js'
import Modal from './components/Modal.vue'
import Alert from './components/Alert.vue'
import {useModalStore,useIdentityStore,useAlertStore,useLoadingStore} from './stores/store.js'

onMounted(() => {
  if (sessionStorage.getItem("Authentication-Token")) {
    useIdentityStore().identity = JSON.parse(sessionStorage.getItem("Identity")) || ['Unauthenticated']
  }
})

function changetheme(value) {
  if (value == 'dark') {
    document.body.setAttribute("data-bs-theme", "dark")
    document.getElementById("searchbutton").classList.remove('btn-outline-dark')
    document.getElementById("searchbutton").classList.add('btn-outline-light')
  }
  else {
    document.body.setAttribute("data-bs-theme", "light")
    document.getElementById("searchbutton").classList.remove('btn-outline-light')
    document.getElementById("searchbutton").classList.add('btn-outline-dark')
  }
}

const navbg = computed(() => {
  if (useIdentityStore().identity.includes('Unauthenticated'))
    return '#5e6eed'
  else if (useIdentityStore().identity.includes('Admin'))
    return '#1a55e3'
  else
    return '#248afd'
})

</script>

<template>

  <nav class="navbar navbar-expand-lg" :style="{ backgroundColor: navbg }">
    <div class="container-fluid">

      <RouterLink class="nav-link" to="/">
        <i class="bi bi-book"></i>BookLit
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#Navbar">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="offcanvas offcanvas-end" tabindex="-1" id="Navbar">

        <div class="offcanvas-header">
          <h5 class="offcanvas-title" id="offcanvasNavbarLabel">
            <RouterLink class="nav-link" to="/">
              <i class="bi bi-book"></i>BookLit
            </RouterLink>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>

        <div class="offcanvas-body">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li v-if="!useIdentityStore().identity.includes('Unauthenticated')" class="nav-item">
              <RouterLink class="nav-link" to="/accountdetails">Account Details</RouterLink>
            </li>

            <li v-if="useIdentityStore().identity.includes('Admin')" class="nav-item">
              <RouterLink class="nav-link" to="/admin/dashboard">Librarian Dashboard</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('Admin')" class="nav-item">
              <RouterLink class="nav-link" to="/admin/books">Books</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('Admin')" class="nav-item">
              <RouterLink class="nav-link" to="/admin/sections">Sections</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('Admin')" class="nav-item">
              <RouterLink class="nav-link" to="/admin/users">Users</RouterLink>
            </li>

            <li v-if="useIdentityStore().identity.includes('User')" class="nav-item">
              <RouterLink class="nav-link" to="/user/dashboard">User Dashboard</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('User')" class="nav-item">
              <RouterLink class="nav-link" to="/user/issuedbooks">Issued Books</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('User')" class="nav-item">
              <RouterLink class="nav-link" to="/user/purchasedbooks">Purchased Books</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('User')" class="nav-item">
              <RouterLink class="nav-link" to="/user/rating">Ratings</RouterLink>
            </li>
            
            <li v-if="!useIdentityStore().identity.includes('Unauthenticated')" class="nav-item">
              <RouterLink id="logout" to="#logout" class="nav-link" @click="useModalStore().modalfunc(logout)" >
                <i class="bi bi-box-arrow-right"></i>Logout
              </RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('Unauthenticated')" class="nav-item">
              <RouterLink id="login" to="#login" class="nav-link" @click="useModalStore().modalfunc(login)"  >Login</RouterLink>
            </li>
            <li v-if="useIdentityStore().identity.includes('Unauthenticated')" class="nav-item">
              <RouterLink id="register" to="#register" class="nav-link" @click="useModalStore().modalfunc(register)" >Register</RouterLink>
            </li>

            <li class="nav-item">
              <RouterLink class="nav-link" to="/policies">Policies</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/random">
                <i class="bi bi-shuffle"></i>Random
              </RouterLink>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                Change theme
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" @click="changetheme('dark')"><i class="bi bi-lightbulb"></i> Dark</a></li>
                <li><a class="dropdown-item" href="#" @click="changetheme('light')"><i class="bi bi-lightbulb-fill"></i> Light</a></li>
              </ul>
            </li>
          </ul>
          <form class="d-flex">
            <input class="form-control me-2" type="search" id="bybook" placeholder="Book Name">
            <button id="searchbutton" class="btn btn-outline-dark" type="submit">Search</button>
          </form>
        </div>

      </div>
    </div>
  </nav>
 
  <div v-if="useLoadingStore().loading" class="modal-backdrop fade show">
    <div class="spinner-grow text-primary position-absolute top-50 start-50 translate-middle" style="width: 3rem; height: 3rem;" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>

  <Alert :alerts="useAlertStore().alerts"></Alert>
  <Modal :modal="useModalStore().modal"></Modal>
  <RouterView />
</template>