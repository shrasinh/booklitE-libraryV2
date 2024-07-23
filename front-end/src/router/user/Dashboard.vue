<script setup>
    import Stats from './dashboard_view/Stats.vue'
    import Delete from './dashboard_view/Delete.vue'
    import Payment from './dashboard_view/Payment.vue'
    import Account from './dashboard_view/Account.vue'
    import Membership from './dashboard_view/Membership.vue'
    import { onBeforeRouteLeave } from 'vue-router'
    import { onMounted, ref } from 'vue'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import { useLoadingStore } from '../../stores/store.js'

    const user = ref( null )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "user/dashboard" )
        if ( r.ok )
        {
            r = await r.json()
            user.value = r
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

    <ul class="nav nav-tabs flex-column flex-lg-row justify-content-end">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#stats">Usage
                stats</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#account">Account details</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#payment">Payment
                details</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#membership">Membership
                details</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#delete">Delete account</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade active show" id="stats">
            <Stats v-if="user" :user="user"></Stats>
        </div>
        <div class="tab-pane fade" id="account">
            <Account v-if="user" :user="user"></Account>
        </div>
        <div class="tab-pane fade" id="payment">
            <Payment v-if="user" :user="user"></Payment>
        </div>
        <div class="tab-pane fade" id="membership">
            <Membership v-if="user" :user="user"></Membership>
        </div>
        <div class="tab-pane fade" id="delete">
            <Delete v-if="user" :user="user"></Delete>
        </div>
    </div>

</template>
