<script setup>
    import { useLoadingStore } from '../stores/store.js'
    defineProps( [ 'spin' ] )
</script>

<template>
    <div v-if="useLoadingStore().loading" class="modal-backdrop fade show">
        <div class="spinner-grow text-primary position-absolute top-50 start-50 translate-middle"
            style="width: 3rem; height: 3rem;"></div>
        <div class="spinner-grow text-primary position-absolute top-50 start-50" style="width: 3rem; height: 3rem;">
        </div>
        <div class="spinner-grow text-primary position-absolute end-50 top-50" style="width: 3rem; height: 3rem;"></div>
    </div>
</template>