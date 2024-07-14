<script setup>
    import { onMounted, ref } from 'vue'
    import { RouterLink } from 'vue-router'
    import { useLoadingStore, useAlertStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import Filter from '../../components/Filter.vue'


    const purchases = ref( [] )
    const filter = ref( "section" )
    const search = ref( "" )
    function result ( purchase )
    {
        return search.value.length > 0 ?
            ( filter.value == 'book' ? purchase.book_name.toLowerCase().includes( search.value.toLowerCase() ) :
                ( filter.value == 'author' ? purchase.author_name.toLowerCase().includes( search.value.toLowerCase() ) :
                    ( purchase.section_name.toLowerCase().includes( search.value.toLowerCase() )
                    ) ) ) : true
    }

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "user/purchase" )
        if ( r.ok )
        {
            r = await r.json()
            purchases.value = r.purchases
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

    async function download ( storage, name )
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( storage + '?type=download' )
        if ( r.ok )
        {
            useAlertStore().alertpush( [ { msg: 'The book downloading has started!', type: 'alert-info' } ] )

            const pdfblob = await r.blob()
            const pdfURL = URL.createObjectURL( pdfblob ) //assign a url to the blob object that can used by anchor tag to download the content
            const anchor = document.createElement( "a" )
            anchor.href = pdfURL
            anchor.download = name + '.pdf'
            document.body.appendChild( anchor )
            anchor.click()
            document.body.removeChild( anchor )
            URL.revokeObjectURL( pdfURL )
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

    <div class="row table-responsive p-4">
        <div class='row mb-4 justify-content-between align-items-center'>
            <div class="col-auto">
                <h1>Purchases</h1>
            </div>
            <div class="col-auto" v-show="purchases.length>0">
                <div class="row">
                    <div class="col-auto">
                        <Filter v-model="filter"></Filter>
                    </div>
                    <div class="col">
                        <input class="form-control search-icon" placeholder="Search..." v-model="search">
                    </div>
                </div>
            </div>
        </div>
        <p v-if="purchases.length===0" class="text-muted">
            You have not yet purchased any books. All your purchased books will be available in this
            section.</p>
        <table v-else class="table table-bordered">
            <tbody>
                <tr v-for="purchase in purchases" :key="purchase.purchase_id">
                    <td class="row align-items-center mb-3 mt-3" v-if="result(purchase)">
                        <div class="col-lg-2 row">
                            <img :src="purchase.thumbnail" class="img-thumbnail"
                                style="max-height:200px;max-width:200px">
                        </div>
                        <div class="col-lg row mt-2">
                            <div class="row"><span><code>Book: </code>
                                    <RouterLink :to="`/book/${purchase.book_id}`">{{ purchase.book_name }}</RouterLink>
                                </span>
                            </div>
                            <div class="row"><span><code>Section:</code> {{ purchase.section_name }}</span></div>
                            <div class="row"><span><code>Author:</code> {{ purchase.author_name }}</span></div>
                            <div class="row"><span><code>Issue Date:</code> {{ purchase.purchase_date }}</span></div>
                            <div class="row">
                                <span><code>Price:</code> &#8377;{{ purchase.price }}</span>
                            </div>
                            <div class="row column-gap-3 mt-3">
                                <span class="col-auto">
                                    <button @click="()=>download(purchase.storage,purchase.book_name)"
                                        :title="`download ${purchase.book_name}`" class="btn btn-outline-success">
                                        <i class="bi bi-download pointer-link"></i> Download!
                                    </button>
                                </span>
                            </div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

</template>
