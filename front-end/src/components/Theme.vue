<script setup>
  import { useThemeStore } from '../stores/store.js'
  import { storeToRefs } from 'pinia'

  const { theme } = storeToRefs( useThemeStore() )

  function changetheme ( value )
  {
    if ( value == 'dark' )
    {
      document.body.setAttribute( "data-bs-theme", "dark" )
      theme.value = 'dark'
    }
    else
    {
      document.body.setAttribute( "data-bs-theme", "light" )
      theme.value = 'light'
    }
  }
</script>
<template>
  <div class="dropdown" title="change the theme of the site">
    <a class="nav-link pointer-link dropdown-toggle d-flex align-items-center" data-bs-toggle="dropdown">
      <i v-if="theme=='dark'" class="bi bi-lightbulb"></i>
      <i v-else class="bi bi-lightbulb-fill"></i>
    </a>
    <ul class="dropdown-menu dropdown-menu-end">
      <li>
        <button :class="['pointer-link','dropdown-item','d-flex','align-items-center',(theme=='dark')&&'active']"
          @click="changetheme('dark')">
          <i class="bi bi-lightbulb me-2"></i> Dark
          <i v-if="theme=='dark'" class="bi bi-check2 ms-auto"></i>
        </button>
      </li>
      <li>
        <button :class="['pointer-link','dropdown-item','d-flex','align-items-center',(theme=='light')&&'active']"
          @click="changetheme('light')">
          <i class="bi bi-lightbulb-fill me-2"></i> Light
          <i v-if="theme=='light'" class="bi bi-check2 ms-auto"></i>
        </button>
      </li>
    </ul>
  </div>
</template>