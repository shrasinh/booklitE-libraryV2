<script setup>
    import { onMounted, ref } from 'vue';
    import { useSearchStore, useLoadingStore } from '../stores/store.js'
    import { fetchfunct, checkerror } from '../components/fetch.js'
    import { storeToRefs } from 'pinia'
    import Filter from './Filter.vue'
    import Starrating from './Starrating.vue';

    const { sections } = storeToRefs( useSearchStore() )
    const filter = ref( "section" )
    const value = ref( "" )
    const results = ref( 0 )


    // for getting the number of results as the search output
    function result_count ()
    {
        if ( filter.value == "section" )
        {
            results.value = document.querySelectorAll( '.section' ).length
        }
        else
        {
            results.value = document.querySelectorAll( '.book-author' ).length
        }
    }


    async function value_load ()
    {
        if ( sections.value.length == 0 )
        {
            useLoadingStore().loading = true
            let r = await fetchfunct( backurl )
            if ( r.ok )
            {
                r = await r.json()
                sections.value = r.sections
                useSearchStore().book_ids = r.book_ids
            }
            else
            {
                checkerror( r )
            }
            // stopping the loading screen
            useLoadingStore().loading = false

        }

    }

    onMounted( () =>
    {
        document.getElementById( 'searchModal' ).addEventListener( 'show.bs.modal', value_load )
        new MutationObserver( result_count ).observe( document.getElementById( 'searchModal' ), { subtree: true, childList: true } )
    } )

</script>
<template>
    <div class="modal fade" id="searchModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="row column-gap-1 align-items-center" style="width:100%">
                        <div class="col-auto">
                            <Filter v-model="filter"></Filter>
                        </div>
                        <div class="col-9"><input class="form-control search-icon" v-model="value"
                                placeholder="Search in the library" type="search"></div>
                    </div>
                </div>
                <div class="modal-body">
                    <div class="text-muted mb-3" v-show="value.length>0&&filter.length>0">{{ results }} search results
                        for
                        {{ filter }}.
                    </div>
                    <ul class='list-group'>
                        <div v-for="section in sections" :key="section.section_id">
                            <li class="list-group-item section"
                                v-if="value.length>0?(filter=='section'?section.section_name.toLowerCase().includes(value.toLowerCase()):true):true">
                                Section: {{ section.section_name }}
                                <ul class="list-group" v-for="book in section.books" :key="book.book_id">
                                    <RouterLink :to="'/book/'+book.book_id"
                                        class="list-group-item list-group-item-action book-author"
                                        v-if="value.length>0?(filter=='book'?book.book_name.toLowerCase().includes(value.toLowerCase()):(filter=='author'?book.author_name.toLowerCase().includes(value.toLowerCase()):true)):true">
                                        <div class="row">
                                            <div class="col-auto">
                                                <img :src="book.thumbnail" class="img-fluid img-thumbnail">
                                            </div>
                                            <div class="col-auto">
                                                <div>
                                                    <Starrating :rating="book.rating"></Starrating>
                                                </div>
                                                <div>Book: {{ book.book_name }}</div>
                                                <div>Author: {{ book.author_name }}</div>
                                            </div>
                                        </div>
                                    </RouterLink>
                                </ul>
                            </li>
                        </div>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .modal-content {
        min-height: 250px
    }

    .img-thumbnail {
        max-width: 100px
    }
</style>
