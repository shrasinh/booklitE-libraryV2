<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { reactive,nextTick } from 'vue';
import Modal from './components/Modal.vue'
import * as bootstrap from "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.esm.min.js"
import {h,render} from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

const modal = reactive({})
window.bootstrap=bootstrap
async function modalfunc(value) {
  if (value == 'register') {
    modal.id = 'registerModal'
    modal.title = 'Let\'s Get You Signed Up.'
    modal.body = h('form', [
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', minlength: '4', maxlength: '32', placeholder: 'Username', required: true })),
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', type: 'email', placeholder: 'Email Address', required: true })),
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', type:'password', minlength: '8', placeholder: 'Password', required: true })),
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', type: 'password', minlength: '8', placeholder: 'Reconfirm password', required: true })),
      h('div', { class: 'd-grid gap-2' }, h('input', { class: 'btn btn-outline-primary', type: 'submit' })),
    ])
    modal.footer = h('a', { href: "#login", async onClick() {  modalfunc('login') }, 'data-bs-toggle': "modal" }, "Already have an account? Login")
  }
  else if (value == 'login') { 
    modal.id = 'loginModal'
    modal.title = 'Welcome Back!'
    modal.body = h('form', [
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', minlength: '4', maxlength: '32', placeholder: 'Username', required: true })),
      h('div', { class: 'mb-3' }, h('input', { class: 'form-control', type: 'password', minlength: '8', placeholder: 'Password', required: true })),
      h('div'),h('div'),
      h('div', { class: 'd-grid gap-2' }, h('input', { class: 'btn btn-outline-primary', type: 'submit' })),
    ])
    modal.footer = h('a', { href: "#register", onClick() { modalfunc('register') }, 'data-bs-toggle': "modal" }, "New user? Register")
  }
  else {
    modal.id = 'logoutModal'
    modal.title = 'Good Bye!'
    modal.body = h('div','Do you want to logout?')
    modal.footer = h('button', { class: 'btn btn-secondary' },'Confirm')
  }
  await nextTick()
  const l = new bootstrap.Modal(document.getElementById(modal.id))
  document.addEventListener('closeModal', () => { 
        l.hide();
    });
  console.log(l)
  l.show()
}  
</script>

<template>
    <nav class="navbar navbar-expand-lg bg-primary">
      <div class="container-fluid">
          <RouterLink class="nav-link" to="/">
            <i class="bi bi-book"></i>BookLit
          </RouterLink>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#basenavbar">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="basenavbar">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/accountdetails">Account Details</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/dashboard">Librarian Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/books">Books</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/sections">Sections</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/users">Users</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/dashboard">User Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/issuedbooks">Issued Books</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/purchasedbooks">Purchased Books</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/rating">Ratings</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/policies">Policies</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/random">
                <i class="bi bi-shuffle"></i>Random
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink id="logout" to="#logout" class="nav-link" @click="modalfunc('logout')" data-bs-toggle="modal">
                <i class="bi bi-box-arrow-right"></i>Logout
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink id="login" to="#login" class="nav-link" @click="modalfunc('login')" data-bs-toggle="modal" >Login</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink id="register" to="#register" class="nav-link" @click="modalfunc('register')" data-bs-toggle="modal" >Register</RouterLink>
          </li>
        </ul>
          <input class="form-control me-2" type="search" id="bybook" placeholder="Book Name">
          <button class="btn btn-outline-dark" type="submit">Search</button>
      </div>
    </div>
  </nav>
  <Modal :modal="modal"></Modal>
  <RouterView />
</template>

