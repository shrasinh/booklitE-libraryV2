<script setup>
    import { onMounted, ref, h } from 'vue'
    import { RouterLink } from 'vue-router'
    import { useLoadingStore, useModalStore } from '../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import Bookview from '../../components/Bookview.vue'
    import Filter from '../../components/Filter.vue'
    import { onBeforeRouteLeave } from 'vue-router'

    onBeforeRouteLeave( () =>
    {
        bootstrap.Tab.getOrCreateInstance( document.querySelector( 'button[data-bs-target="#current"]' ) ).show()
    } )

    const previous_issue = ref( [] )
    const current_issue = ref( [] )
    const previous_filter = ref( "section" )
    const current_filter = ref( "section" )
    const current_search = ref( "" )
    const previous_search = ref( "" )
    function current_result ( issue )
    {
        return current_search.value.length > 0 ?
            ( current_filter.value == 'book' ? issue.book_name.toLowerCase().includes( current_search.value.toLowerCase() ) :
                ( current_filter.value == 'author' ? issue.author_name.toLowerCase().includes( current_search.value.toLowerCase() ) :
                    ( issue.section_name.toLowerCase().includes( current_search.value.toLowerCase() )
                    ) ) ) : true
    }
    function previous_result ( issue )
    {
        return previous_search.value.length > 0 ?
            ( previous_filter.value == 'book' ? issue.book_name.toLowerCase().includes( previous_search.value.toLowerCase() ) :
                ( previous_filter.value == 'author' ? issue.author_name.toLowerCase().includes( previous_search.value.toLowerCase() ) :
                    ( issue.section_name.toLowerCase().includes( previous_search.value.toLowerCase() )
                    ) ) ) : true
    }

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "user/issue" )
        if ( r.ok )
        {
            r = await r.json()
            previous_issue.value = r.previous_issue
            current_issue.value = r.current_issue
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

    function returnbookmodal ( book_id, book_name, issue_id )
    {
        const returnModal = {
            id: 'returnModal',
            title: 'Book return confirmation',
            body: h( 'span', [ 'Are you sure you want return ',
                h( RouterLink, { to: `/book/${ book_id }`, onClick: () => bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide() }, book_name ),
                ' ? You can issue it again any time.'
            ] ),
            footer: h( 'button', { class: 'btn btn-warning', onClick: () => returnbook( issue_id ) }, 'Confirm' )
        }

        useModalStore().modalfunc( returnModal )

    }

    async function returnbook ( issue_id )
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + `/user/issue/return/${ issue_id }` )
        if ( r.ok )
        {   //adjusting the values of returned book
            for ( const i in current_issue.value )
            {
                if ( current_issue.value[ i ].issue_id == issue_id )
                {
                    current_issue.value[ i ].return_date = new Date().toUTCString()
                    previous_issue.value.push( { ...current_issue.value[ i ] } )
                    current_issue.value.splice( i, 1 )
                    break
                }
            }

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
    <ul class="nav nav-tabs justify-content-end">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#current">Current issues</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#previous">Previous issues</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade active show" id="current">
            <div class="row table-responsive p-4">
                <div class='row mb-4 justify-content-between align-items-center'>
                    <div class="col-auto">
                        <h1>Current issues</h1>
                    </div>
                    <div class="col-auto" v-show="current_issue.length>0">
                        <div class="row">
                            <div class="col-auto">
                                <Filter v-model="current_filter"></Filter>
                            </div>
                            <div class="col">
                                <input class="form-control search-icon" placeholder="Search..."
                                    v-model="current_search">
                            </div>
                        </div>
                    </div>
                </div>
                <p v-if="current_issue.length===0" class="text-muted">
                    You have not currently issued any books. All your currently issued books will be visible in this
                    section.</p>
                <table v-else class="table table-bordered">
                    <tbody>
                        <tr v-for="issue in current_issue" :key="issue.issue_id">
                            <td class="row align-items-center mb-3 mt-3" v-if="current_result(issue)">
                                <div class="col-lg-2 row">
                                    <img :src="issue.thumbnail" class="img-thumbnail"
                                        style="max-height:200px;max-width:200px">
                                </div>
                                <div class="col-lg row mt-2">
                                    <div class="row"><span><code>Book: </code>
                                            <RouterLink :to="`/book/${issue.book_id}`">
                                                {{ issue.book_name }}
                                            </RouterLink>
                                        </span>
                                    </div>
                                    <div class="row"><span><code>Section:</code> {{ issue.section_name }}</span></div>
                                    <div class="row"><span><code>Author:</code> {{ issue.author_name }}</span></div>
                                    <div class="row"><span><code>Issue Date:</code> {{ issue.issue_date }}</span></div>
                                    <div class="row">
                                        <span><code>Return Date:</code> {{ issue.return_date }}</span>
                                    </div>
                                    <div class="row column-gap-3 mt-3">
                                        <span class="col-auto">
                                            <Bookview :url="issue.storage" :language="issue.language"
                                                :id="`issue${issue.issue_id}`" :book_name="issue.book_name"
                                                :icon="true"></Bookview>
                                        </span>
                                        <span class="col-auto">
                                            <button class="btn btn-outline-danger" :title="`return ${issue.book_name}`"
                                                @click="()=>returnbookmodal(issue.book_id,issue.book_name,issue.issue_id)">
                                                <i class="bi bi-journal-arrow-up pointer-link"></i> Return!
                                            </button>
                                        </span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class=" tab-pane fade" id="previous">
            <div class="row table-responsive p-4">
                <div class='row mb-4 justify-content-between align-items-center'>
                    <div class="col-auto">
                        <h1>Previous issues</h1>
                    </div>
                    <div class="col-auto" v-show="previous_issue.length>0">
                        <div class="col-auto">
                            <div class="row">
                                <div class="col-auto">
                                    <Filter v-model="previous_filter"></Filter>
                                </div>
                                <div class="col">
                                    <input class="form-control search-icon" placeholder="Search..."
                                        v-model="previous_search">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <p v-if="previous_issue.length==0" class="text-muted">
                    You do not have any books. Once you return a book, it is going to be visible
                    in this section.</p>
                <table v-else class="table table-bordered">
                    <tbody>
                        <tr v-for="issue in previous_issue" :key="issue.issue_id">
                            <td class="row align-items-center mb-3 mt-3" v-if="previous_result(issue)">
                                <div class="col-lg-2 row">
                                    <img :src="issue.thumbnail" class="img-thumbnail"
                                        style="max-height:200px;max-width:200px">
                                </div>
                                <div class="col-lg row mt-2">
                                    <div class="row"><span><code>Book: </code>
                                            <RouterLink :to="`/book/${issue.book_id}`">
                                                {{ issue.book_name }}
                                            </RouterLink>
                                        </span>
                                    </div>
                                    <div class="row"><span><code>Section:</code> {{ issue.section_name }}</span></div>
                                    <div class="row"><span><code>Author:</code> {{ issue.author_name }}</span></div>
                                    <div class="row"><span><code>Issue Date:</code> {{ issue.issue_date }}</span></div>
                                    <div class="row">
                                        <span><code>Return Date:</code> {{ issue.return_date }}</span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</template>
