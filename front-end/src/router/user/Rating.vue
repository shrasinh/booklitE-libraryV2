<script setup>
    import { onMounted, ref } from 'vue'
    import { useLoadingStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import { onBeforeRouteLeave } from 'vue-router'
    import Notrated from './rating_view/Notrated.vue'
    import Rated from './rating_view/Rated.vue'

    const rating = ref( null )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "user/ratings" )
        if ( r.ok )
        {
            r = await r.json()
            rating.value = r
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )
    onBeforeRouteLeave( () =>
    {
        bootstrap.Tab.getOrCreateInstance( document.querySelector( 'button[data-bs-target="#rated"]' ) ).show()
    } )

</script>

<template>

    <ul class="nav nav-tabs justify-content-end">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#rated">Rated books</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#not_rated">Not rated books</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade active show" id="rated">
            <Rated v-if="rating" :rating="rating"></Rated>
        </div>
        <div class="tab-pane fade" id="not_rated">
            <Notrated v-if="rating" :rating="rating"></Notrated>
        </div>
    </div>
</template>