<script setup>
    import Stats from './dashboard_view/Stats.vue'
    import Export from './dashboard_view/Export.vue'
    import { onBeforeRouteLeave } from 'vue-router'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import { onMounted, ref } from 'vue'
    import { useLoadingStore } from '../../stores/store.js'

    const admin = ref( null )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/dashboard" )
        if ( r.ok )
        {
            r = await r.json()
            admin.value = r
        }
        else
        {
            checkerror( r )
        }
        useLoadingStore().loading = false
    } )

    onBeforeRouteLeave( () =>
    {
        bootstrap.Tab.getOrCreateInstance( document.querySelector( 'button[data-bs-target="#stats"]' ) ).show()
    } )
</script>

<template>

    <ul class="nav nav-tabs justify-content-end">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#stats">Library
                stats</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#export">Export library
                details</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade active show" id="stats">
            <Stats v-if="admin" :admin="admin"></Stats>
        </div>
        <div class="tab-pane fade" id="export">
            <Export v-if="admin"></Export>
        </div>
    </div>

</template>