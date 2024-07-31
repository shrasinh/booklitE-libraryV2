<script setup>
    import { onMounted, ref, h } from 'vue'
    import { storeToRefs } from 'pinia'
    import { RouterLink } from 'vue-router'
    import { useAlertStore, useLoadingStore, useModalStore, useBookcreateStore, useBookdetailsStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import Bookedit from './Bookedit.vue'

    const books = ref( [] )
    const { sections, languages } = storeToRefs( useBookcreateStore() )
    const search = ref( "" )
    const checked = ref( [] )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/books" )
        if ( r.ok )
        {
            r = await r.json()
            books.value = r.books
            useBookdetailsStore().books = { ...r.books }
            sections.value = r.sections
            languages.value = r.languages
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

    function deletebookchecking ()
    {
        if ( checked.value.length != 0 )
        {
            const deletebookModal = {
                id: 'deletebookModal',
                title: 'Book delete confirmation',
                body: h( 'div', [ h( 'p', 'Are you sure you want to delete the following books along with any data associated with them?' ),
                h( 'ul', checked.value.map( ( id => h( 'li', `Book ID: ${ id }` ) ) ) ) ] ),
                footer: h( 'button', { class: 'btn btn-danger', onClick: () => deletebook() }, 'Confirm' )
            }

            useModalStore().modalfunc( deletebookModal )

        }

    }

    async function deletebook ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true
        let bodyContent = new FormData()

        bodyContent.append(
            "book_ids", checked.value,
        )
        let r = await fetchfunct( backurl + "admin/books/delete", {
            method: "DELETE", body: bodyContent
        } )
        if ( r.ok )
        {   //removing the deleted books and resetting the checked array
            books.value = books.value.filter( b => !checked.value.includes( b.book_id ) )
            checked.value.length = 0
            useBookdetailsStore().books = { ...books.value }

            //providing feedback
            r = await r.json()
            if ( r.response.errors.length == 0 )
            { useAlertStore().alertpush( [ { msg: 'Selected books are successfully deleted!', type: 'alert-success' } ] ) }
            else
            { useAlertStore().alertpush( r.response.errors.map( e => { return { msg: e, type: 'alert-danger' } } ) ) }
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
    <div class='row mb-3 justify-content-between align-items-center'>
        <div class="col-auto">
            <h1 class="mb-3 p-2">All Books</h1>
        </div>
        <div class="col-auto p-4">
            <input class="form-control search-icon" placeholder="Search for a book..." v-model="search">
        </div>
    </div>

    <p v-if="books.length===0" class="text-muted mb-3 p-2">
        No book added yet.</p>

    <div v-else>
        <div class="row mx-auto mb-3 text-center">
            <div class="col-auto">
                <button class="btn btn-outline-danger" @click="deletebookchecking" title="Delete books"
                    v-show="checked.length!=0"><i class="bi bi-trash3"></i> Delete
                </button>
            </div>
        </div>


        <div class="accordion" id="books">
            <div v-for="book in books" :key="book.book_id">
                <div class="accordion-item"
                    v-if="search.length==0|book.book_name.toLowerCase().includes(search.toLowerCase())">

                    <div class="accordion-header">
                        <div class="row align-items-center">
                            <div class="col-auto ms-4"><input type="checkbox" :value="book.book_id" v-model="checked"
                                    class="form-check-input" title="delete section" />
                            </div>
                            <div class="col">
                                <div class="accordion-button collapsed row" data-bs-toggle="collapse"
                                    :data-bs-target="'#collapse'+book.book_id">
                                    <div class="col-lg-2 row">
                                        <img :src="book.thumbnail" class="img-thumbnail"
                                            style="max-height:200px;max-width:200px">
                                    </div>
                                    <div class="col-lg row">
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Book Id</div>
                                            <div class="col-auto">{{book.book_id}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Book Name</div>
                                            <div class="col-auto">{{book.book_name}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Number of copies available</div>
                                            <div class="col-auto">{{book.no_of_copies_available}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Number of current issues</div>
                                            <div class="col-auto">{{book.currently_issued_by.length}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Total number of issues</div>
                                            <div class="col-auto">{{book.no_of_issues}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Total number of purchases</div>
                                            <div class="col-auto">{{book.no_of_purchase}}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div :id="'collapse'+book.book_id" class="accordion-collapse collapse" data-bs-parent="#books">
                        <div class="accordion-body">
                            <Bookedit :book="book"></Bookedit>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>

    <RouterLink id="bookcreate" to="/admin/books/create" style="z-index:3;bottom:5%;right:5%" class="
        position-fixed">
        <button class=" btn btn-primary rounded-pill" title="Create a new book"><i class="bi bi-plus-lg"></i></button>
    </RouterLink>

</template>
<style scoped>
    #bookcreate button {
        position: relative;
        top: 0;
        transition: top ease 0.5s;
        font-size: 35px;
    }

    #bookcreate:hover button {
        top: -5px;
    }
</style>