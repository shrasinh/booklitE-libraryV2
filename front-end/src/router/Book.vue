<script setup>
    import { onMounted, ref, computed, h } from 'vue';
    import { fetchfunct, checkerror, checksuccess } from '../components/fetch.js'
    import Starrating from '../components/Starrating.vue';
    import { useRouter, useRoute, onBeforeRouteUpdate } from 'vue-router';
    import { useLoadingStore, useModalStore, useIdentityStore, useAlertStore } from '../stores/store';

    const router = useRouter()
    const route = useRoute()
    const props = defineProps( {
        id: String
    } )
    const book = ref( { ratings: [] } )
    const count = computed( () =>
    {
        const rating_count = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
        book.value.ratings.map( e => { rating_count[ e.rating ] += 1 } )
        return rating_count
    } )
    const feedback_present = computed( () =>
    {
        if ( book.value.ratings.length > 0 )
        {
            for ( const i of book.value.ratings )
            {
                if ( i.feedback )
                {
                    return true
                }

            }
            return false
        }
        return false

    } )

    const average = computed( () =>
    {
        if ( book.value.ratings.length > 0 )
        {
            let total = 0
            for ( const i in count.value )
            {
                total += count.value[ i ] * i
            }
            return total / book.value.ratings.length
        }
        return 0

    } )

    async function loaddata ( to = null, from = null )
    {
        if ( ( !to ) || ( to.params.id != from.params.id ) )
        {
            const id = to ? to.params.id : props.id
            if ( !isNaN( id ) )
            {
                useLoadingStore().loading = true
                let r = await fetchfunct( backurl + `book/${ id }` )
                if ( r.ok )
                {
                    r = await r.json()
                    book.value = r
                }
                else
                {
                    router.go( -1 )
                    checkerror( r )
                }
                // stopping the loading screen
                useLoadingStore().loading = false
            }
            else
            {
                router.replace( {
                    name: "Notfound",
                    params: { pathMatch: route.path.substring( 1 ).split( '/' ) }
                } )

            }
        }
    }

    onBeforeRouteUpdate( loaddata )

    onMounted( loaddata )

    function purchasechecking ()
    {
        if ( useIdentityStore().identity.includes( "User" ) )
        {
            const purchaseModal = {
                id: 'purchaseModal',
                title: 'Purchase confirmation',
                body: `Are you sure you want to spend Rs. ${ book.value.price } to purchase ${ book.value.book_name } ?`,
                footer: h( 'button', { class: 'btn btn-success', onClick: () => purchase() }, 'Confirm' )
            }

            useModalStore().modalfunc( purchaseModal )

        }
        else
        {
            useAlertStore().alertpush( [ { msg: 'You donot have sufficient permission for this action! Please login with the correct account.', type: "alert-danger" } ] )
        }

    }

    function issuechecking ()
    {
        if ( useIdentityStore().identity.includes( "User" ) )
        {
            const issueModal = {
                id: 'issueModal',
                title: 'Issue confirmation',
                body: `Are you sure you want to issue ${ book.value.book_name }?`,
                footer: h( 'button', { class: 'btn btn-success', onClick: () => issue() }, 'Confirm' )
            }

            useModalStore().modalfunc( issueModal )

        }
        else
        {
            useAlertStore().alertpush( [ { msg: 'You donot have sufficient permission for this action! Please login with the correct account.', type: "alert-danger" } ] )
        }

    }


    async function purchase ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + `user/book/purchase/${ props.id }` )
        if ( r.ok )
        {
            router.push( "/user/purchase" )
            checksuccess( r )
        }
        else
        {
            checkerror( r )
        }

        // stopping the loading screen
        useLoadingStore().loading = false
    }


    async function issue ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + `user/book/issue/${ props.id }` )
        if ( r.ok )
        {
            router.push( "/user/issue" )
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
    <div class="row column-gap-5">
        <div class="col me-2 ms-2 thumbnail-container" style="max-width:30%">
            <img :src="book.thumbnail" class="img-thumbnail h-100">
        </div>
        <div class="col-lg ms-2 mt-2">
            <div class="row">
                <h1>{{book.book_name}}</h1>
            </div>
            <br>
            <div class="row">
                <p><strong>Author:</strong> {{book.author_name}}</p>
            </div>
            <div class="row">
                <p><strong>Language:</strong> {{book.language}}</p>
            </div>
            <div class="row">
                <h4>About the book</h4>
                <p class="break-word">{{book.description}}</p>
            </div>
            <div class="row">
                <span>
                    <button @click="issuechecking" :disabled="book.no_of_copies_available==0" class="btn btn-warning"
                        title="Issue the book">Issue the
                        book</button>
                </span>
                <p class="text-muted"><em>Available copies: {{book.no_of_copies_available}}</em></p>
            </div>
            <div class="row">
                <span>
                    <button class="btn btn-warning" @click="purchasechecking" title="Purchase the book">Buy the
                        book</button>
                </span>
                <p class="text-muted"><em>Price: &#8377 {{book.price}}</em></p>
            </div>
        </div>
    </div>

    <h1 class="p-2">Ratings & Reviews</h1>
    <div class="row p-2" v-if="book.ratings.length>0">
        <div class="col-lg-4">

            <Starrating :rating="average"></Starrating> average based on {{book.ratings.length}} ratings.

            <div v-for="(value,key) in count" class="row align-items-center mt-3">
                <div class="col-auto">{{key}} star</div>
                <div class="col">
                    <div class="progress" style="width:100%">
                        <div class="progress-bar text-bg-warning"
                            :style="{'width':(value/book.ratings.length)*100+'%'}">
                        </div>
                    </div>
                </div>
                <div class="col-auto">{{value}}</div>
            </div>

        </div>

        <div class="col-lg">
            <div v-for="rating in book.ratings">
                <div v-if="rating.feedback" class="row ms-lg-5 mt-4">
                    <div class="row justify-content-between">
                        <div class="col-auto text-start" title="username">
                            {{rating.username}}
                        </div>
                        <div class="col-auto text-muted text-end" title="rating date">
                            {{rating.rating_date}}
                        </div>
                    </div>
                    <div class="row">
                        <Starrating :rating="rating.rating"></Starrating>
                    </div>
                    <div class="row">
                        <p class="break-word">{{rating.feedback}}</p>
                    </div>
                    <hr>
                </div>
            </div>
            <div v-if="!feedback_present" class="text-muted">No reviews present.</div>
        </div>

    </div>
    <p v-else class="p-2 mb-3 text-muted">There is no ratings yet.</p>
</template>
<style scoped>
    @media (max-width: 1100px) {
        .thumbnail-container {
            max-width: 80% !important;
        }
    }
</style>