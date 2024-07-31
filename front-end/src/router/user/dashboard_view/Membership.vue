<script setup>
    import { RouterLink } from 'vue-router'
    import { h, ref } from 'vue'
    import { useLoadingStore, useModalStore, useIdentityStore, useAlertStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'

    const props = defineProps( [ 'user' ] )
    const user = ref( props.user )

    function memberchecking ()
    {
        if ( Object.keys( user.value.payment ).length > 0 )
        {
            const memberModal = {
                id: 'memberModal',
                title: 'Membership purchase confirmation',
                body: 'Are you sure you want to spend Rs. 1000 for purchasing the library lifetime membership?',
                footer: h( 'button', { class: 'btn btn-success', onClick: () => member() }, 'Confirm' )
            }

            useModalStore().modalfunc( memberModal )
        }
        else
        {
            bootstrap.Tab.getOrCreateInstance( document.querySelector( 'button[data-bs-target="#payment"]' ) ).show()
            useAlertStore().alertpush( [ { msg: 'Please enter your payment details first.', type: 'alert-danger' } ] )
        }

    }
    async function member ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()
        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + "user/membership", {
            method: "POST"
        } )
        if ( r.ok )
        {
            user.value.membership_date = new Date().toString().split( ' GMT' )[ 0 ]
            user.value.membership = 'Subscribed member'
            useIdentityStore().identity = [ 'User', 'Member' ]
            checksuccess( r )
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    }
</script>
<template>
    <div class="row justify-content-center p-4">
        <div class="col-lg-5">
            <h1 class="text-center mb-5">Membership Section</h1>
            <p v-if="user.membership=='Subscribed member'">You are a lifetime subscribed member of the library since
                <em>{{ user.membership_date }}</em>. So
                enjoy all the <RouterLink to="/policies">benefits
                </RouterLink>!!
            </p>
            <p v-else>
                Become a lifetime subscribed member of the library!!
                And enjoy <RouterLink to="/policies">much more benefits.</RouterLink>
                <em> Just at &#8377 1000!!</em>
            <div class="mt-5"><button class="btn btn-outline-success" @click="memberchecking">Click here to become a
                    member.</button>
            </div>
            </p>
        </div>
    </div>
</template>