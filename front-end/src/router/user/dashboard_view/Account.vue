<script setup>
    import { ref } from 'vue'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'
    import { useLoadingStore } from '../../../stores/store.js'

    const props = defineProps( [ 'user' ] )
    const user = ref( props.user )

    async function remainder ()
    {
        useLoadingStore().loading = true
        let url = user.value.daily_remainders ? backurl + "user/dailymails?options=out" : backurl + "user/dailymails"
        let r = await fetchfunct( url )
        if ( r.ok )
        {
            checksuccess( r )
            user.value.daily_remainders = user.value.daily_remainders ? false : true
        }
        else
        {
            checkerror( r )
        }
        useLoadingStore().loading = false
    }

    function member_tab ()
    {
        bootstrap.Tab.getOrCreateInstance( document.querySelector( 'button[data-bs-target="#membership"]' ) ).show()
    }
</script>

<template>
    <h1 class="mb-3 text-center p-4">Account details</h1>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Username:</div>
        <div class="col-md-4 col break-word">{{user.username}}</div>
    </div>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Email:</div>
        <div class="col-md-4 col break-word">{{user.email}}</div>
    </div>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Last login at:</div>
        <div class="col-md-4 col break-word">{{user.last_login_at}}</div>
    </div>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Last login ip:</div>
        <div class="col-md-4 col break-word">{{user.last_login_ip}}</div>
    </div>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Membership type:</div>
        <div class="col-md-4 col break-word">
            <span v-if="user.membership=='Normal member'" class="ms-1">Normal Member
                <a class="pointer-link" @click="member_tab" title="Become a subscribed library member">want to be a
                    subscribed member?</a>
            </span>
            <span v-else>
                Subscribed member
            </span>
        </div>
    </div>
    <div class="row mb-3 justify-content-center">
        <div class="col-md-4 col text-end">Daily remainders:</div>
        <div class="col-md-4 col break-word">
            <span v-if="!user.daily_remainders"> Not opted
                <button class="btn btn-outline-primary ms-2" @click="remainder"
                    title="Never miss a day of reading. Opt for daily remainders">Opt</button>
            </span>
            <span v-else class="ms-1"> Opted
                <button class="btn btn-outline-primary ms-2" @click="remainder"
                    title="Never miss a day of reading. Opt for daily remainders">Opt out</button>
            </span>
        </div>
    </div>
</template>