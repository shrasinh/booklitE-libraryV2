<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Modal from './components/Modal.vue'
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
              <RouterLink class="nav-link" to="/policies">Policies</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/random">
                <i class="bi bi-shuffle"></i>Random
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/accountdetails">Account Details</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/dashboard">Librarian Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" href="/user/issuedbooks">Issued Books</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/purchasedbooks">Purchased Books</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/user/rating">Ratings</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" data-bs-toggle="modal" data-bs-target="#logoutModal" to="/logout">
                <i class="bi bi-box-arrow-right"></i>Logout
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/login">Login</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/register">Register</RouterLink>
          </li>

        </ul>
        <form class="d-flex" action="/search" method="get">
          <input class="form-control me-2" type="search" name="bybook" placeholder="Book Name">
          <button class="btn btn-outline-dark" type="submit">Search</button>
        </form>
      </div>
    </div>
  </nav>
  <RouterView />
</template>

