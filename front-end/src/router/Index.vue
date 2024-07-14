<script setup>
  import { onMounted } from 'vue';
  import Carousel from '../components/Carousel.vue'
  import { useLoadingStore, useSearchStore } from '../stores/store.js'
  import { fetchfunct, checkerror } from '../components/fetch.js'
  import { storeToRefs } from 'pinia'
  import { RouterLink } from 'vue-router'
  import Starrating from '../components/Starrating.vue'

  const { sections, book_ids } = storeToRefs( useSearchStore() )


  onMounted( async () =>
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
  } )
</script>

<template>

  <Carousel></Carousel>
  <div class="bg-image p-5 parallax">
    <div class="mask mx-auto p-5 text-center rounded mb-5 text-white border"
      style="background-color: rgba(0, 0, 0, 0.6);width:50%">

      <h1 style="font-family:Courier New, Courier, monospace">BookLit: <h2
          style="font-family:lucida handwriting,brush script,cursive">A Place of Books and Literature</h2>
      </h1>
      <p class="lead" style="font-family:lucida,console, monaco">
        <br><br>
        Search, Issue, Purchase from a variety of top rated collection of Books
        <br>
        written by well-known authors.
        <br><br>
        Listen to the text-to-speech version of the issued books.
        <br><br>
        Become a subscribed member to enjoy an extended issue period <RouterLink to="/policies">and more.</RouterLink>
      </p>
    </div>
  </div>


  <div>
    <h1 class="mb-3 p-2">Sections</h1>
    <p v-if="sections.length===0" class="text-muted p-2">No sections are currently present.<br></p>
    <div v-else>
      <div v-for="section in sections" class="row">
        <div class="row justify-content-between mx-auto">
          <div class="col break-word text-start">
            <h3 :title="section.description">
              <strong>{{section.section_name}}</strong>
            </h3>
          </div>
          <div class="col-md text-md-end text-muted">Date created:{{section.created_on}}</div>
        </div>
        <hr>
        <div class="row row-cols-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6">
          <div v-for="book in section.books" class="col ms-3 me-3">
            <RouterLink class="book h-100 d-flex flex-column" :to="'/book/'+book.book_id">
              <div class="row flex-grow-1">
                <img :src="book.thumbnail" class="img-thumbnail">
              </div>
              <div class="row h-25">
                <Starrating class="Stars-container" :rating="book.rating"></Starrating>
                <div class="row break-word"><span>Book: {{ book.book_name }}</span></div>
                <div class="row break-word"><span>Author: {{book.author_name}}</span></div>
                <div class="row break-word"><span>Language: {{book.language}}</span></div>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>
<style scoped>
  .parallax {
    background-image: url('https://en.idei.club/uploads/posts/2023-06/1687399608_en-idei-club-p-indian-library-dizain-krasivo-4.jpg');
    background-attachment: fixed;
    background-repeat: no-repeat;
  }

  .book {
    text-decoration: none;
    color: var(--bs-emphasis-color)
  }

  .book:visited {
    color: blueviolet
  }

  .book:hover {
    color: var(--navbar-bg)
  }

  .mask {
    border-color: var(--navbar-bg) !important;
  }

  @media (max-width: 1036px) {
    .mask {
      width: 70% !important;
    }
  }

  @media (max-width: 780px) {
    .mask {
      width: 100% !important;
    }
  }

  @media (max-width: 690px) {
    .Stars-container {
      font-size: 170% !important;
    }
  }

</style>