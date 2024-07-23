<script setup>
    import { useRouter } from 'vue-router'
    import { h } from 'vue'
    import { useLoadingStore, useModalStore, useIdentityStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'

    const router = useRouter()
    function accountdeletechecking ()
    {
        const accountdeleteModal = {
            id: 'aacountdeleteModal',
            title: 'Account delete confirmation',
            body: h( 'div', [ h( 'div', { class: 'mb-3' }, h( 'b', 'Please read the below text carefully:' ) ),
                'Are you absolutely sure that you want to delete your account? There is no going back after you press the below button.' ] ),
            footer: h( 'button', { class: 'btn btn-danger', onClick: () => deleteaccount() }, 'I confirm' )
        }

        useModalStore().modalfunc( accountdeleteModal )

    }
    async function deleteaccount ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()
        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + "user/delete", {
            method: "DELETE"
        } )
        if ( r.ok )
        {
            localStorage.removeItem( 'Authentication-Token' )
            localStorage.removeItem( 'Identity' )
            useIdentityStore().identity = [ 'Unauthenticated' ]
            router.push( '/' )
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
    <div class="p-4 text-center row justify-content-center">
        <div class="col-lg-5">
            <h1 class="mb-5">Delete your account</h1>
            <div class="rounded" style="background-color: rgba(159 151 151 / 10%);border: 1px solid var(--navbar-bg);">
                <div class="mt-3">If you want to delete your account, click on the button below. But be absolutely sure
                    as account deletion is a permanent process. </div>
                <div class="mt-3 mb-3"><button class="btn btn-outline-danger" @click="accountdeletechecking">Delete
                        my account</button>
                </div>
            </div>
        </div>
    </div>
</template>