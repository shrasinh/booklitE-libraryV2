<script setup>
    import { ref, h } from 'vue'
    import { RouterLink } from 'vue-router'
    import { useLoadingStore, useModalStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'
    import Ratinggive from './Ratinggive.vue'
    import Filter from '../../../components/Filter.vue'
    import Starrating from '../../../components/Starrating.vue'

    const props = defineProps( [ 'rating' ] )

    const rated = ref( props.rating.rated )
    const not_rated = ref( props.rating.not_rated )

    const search = ref( "" )
    const filter = ref( "section" )
    function result ( rated )
    {
        return search.value.length > 0 ?
            ( filter.value == 'book' ? rated.book_name.toLowerCase().includes( search.value.toLowerCase() ) :
                ( filter.value == 'author' ? rated.author_name.toLowerCase().includes( search.value.toLowerCase() ) :
                    ( rated.section_name.toLowerCase().includes( search.value.toLowerCase() )
                    ) ) ) : true
    }
    function deleteratingchecking ( book_id, book_name, rating_id )
    {
        const deleteratingModal = {
            id: 'deleteratingModal',
            title: 'Rating delete confirmation',
            body: h( 'span', [ h( 'span', 'Are you sure you want delete the rating for ' ),
            h( RouterLink, { to: `/book/${ book_id }`, onClick: () => bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide() }, book_name ),
            h( 'span', ' ? You can rate it again any time.' )
            ] ),
            footer: h( 'button', { class: 'btn btn-danger', onClick: () => deleterating( rating_id ) }, 'Confirm' )
        }

        useModalStore().modalfunc( deleteratingModal )

    }

    async function deleterating ( rating_id )
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true

        let r = await fetchfunct( backurl + "user/ratings/delete/" + rating_id, {
            method: "DELETE"
        } )
        if ( r.ok )
        {
            //removing the deleted rating and moving it to not_rated array
            for ( const i in rated.value )
            {
                if ( rated.value[ i ].rating_id == rating_id )
                {
                    delete rated.value[ i ][ 'rating_id' ]
                    delete rated.value[ i ][ 'rating' ]
                    delete rated.value[ i ][ 'feedback' ]
                    delete rated.value[ i ][ 'rating_date' ]
                    not_rated.value.push( { ...rated.value[ i ] } )
                    rated.value.splice( i, 1 )
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
    <div class='row p-4 mb-3 justify-content-between align-items-center'>
        <div class="col-auto">
            <h1>Rated books</h1>
        </div>
        <div class="col-auto" v-show="rated.length>0">
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
    <p v-if="rated.length===0" class="text-muted ms-4">
        You have not yet given any rating. All your ratings will appear in this section.</p>

    <div v-else>
        <div class="accordion" id="ratedlist">
            <div v-for="rate in rated" :key="rate.rating_id">
                <div class="accordion-item" v-if="result(rate)">

                    <div class="accordion-header">
                        <div class="row align-items-center">
                            <div class="col-auto ms-4 delete"><i title="delete rating" class="bi bi-trash3-fill"
                                    @click="()=>deleteratingchecking(rate.book_id, rate.book_name, rate.rating_id)"></i>
                            </div>
                            <div class="col">
                                <div class="accordion-button collapsed row" data-bs-toggle="collapse"
                                    :data-bs-target="'#collapserate'+rate.rating_id">
                                    <div class="col-lg-2 row">
                                        <img :src="rate.thumbnail" class="img-thumbnail"
                                            style="max-height:200px;max-width:200px">
                                    </div>
                                    <div class="col-lg row">
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Rated</div>
                                            <div class="col-auto">
                                                <Starrating :rating="rate.rating"></Starrating>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Book</div>
                                            <div class="col-auto">
                                                <RouterLink :to="'/book/'+rate.book_id"
                                                    @click="event.stopPropagation()">{{rate.book_name}}
                                                </RouterLink>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Section</div>
                                            <div class="col-auto">{{rate.section_name}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">Author</div>
                                            <div class="col-auto">{{rate.author_name}}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col-lg-4 col-auto">On</div>
                                            <div class="col-auto">{{rate.rating_date}}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div :id="'collapserate'+rate.rating_id" class="accordion-collapse collapse"
                        data-bs-parent="#ratedlist">
                        <div class="accordion-body">
                            <Ratinggive :rating="rate">
                            </Ratinggive>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .delete:hover i {
        color: red
    }
</style>