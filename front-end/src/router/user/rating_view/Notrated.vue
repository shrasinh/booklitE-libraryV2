<script setup>
    import { ref, watch } from 'vue'
    import { RouterLink } from 'vue-router'
    import Ratinggive from './Ratinggive.vue'
    import Filter from '../../../components/Filter.vue'

    const props = defineProps( [ 'rating' ] )

    const rated = ref( props.rating.rated )
    const not_rated = ref( props.rating.not_rated )

    const search = ref( "" )
    const filter = ref( "section" )
    function result ( non_rate )
    {
        return search.value.length > 0 ?
            ( filter.value == 'book' ? non_rate.book_name.toLowerCase().includes( search.value.toLowerCase() ) :
                ( filter.value == 'author' ? non_rate.author_name.toLowerCase().includes( search.value.toLowerCase() ) :
                    ( non_rate.section_name.toLowerCase().includes( search.value.toLowerCase() )
                    ) ) ) : true
    }
    watch( not_rated, () =>
    {
        //removing the not rate value, but now rated and moving it to rated array
        for ( const i in not_rated.value )
        {
            if ( not_rated.value[ i ].rating_id )
            {
                rated.value.push( { ...not_rated.value[ i ] } )
                not_rated.value.splice( i, 1 )
                console.log( rated.value )
                break
            }
        }
    }, { deep: true } )

</script>
<template>
    <div class='row p-4 mb-3 justify-content-between align-items-center'>
        <div class="col-auto">
            <h1>Pending ratings</h1>
        </div>
        <div class="col-auto" v-show="not_rated.length>0">
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
    <p v-if="not_rated.length===0" class="text-muted ms-3 p-2">
        You have no rating pending to give. All the books that you have issue or purchased but have not rated will
        appear in this section.</p>

    <div v-else>
        <div class="accordion" id="nonratedlist">
            <div v-for="non_rate in not_rated" :key="non_rate.book_id">
                <div class="accordion-item" v-if="result(non_rate)">

                    <div class="accordion-header">
                        <div class="row align-items-center">
                            <div class="col">
                                <div class="accordion-button collapsed row" data-bs-toggle="collapse"
                                    :data-bs-target="'#collapsenon'+non_rate.book_id">
                                    <div class="col-lg-2 row">
                                        <img :src="non_rate.thumbnail" class="img-thumbnail"
                                            style="max-height:200px;max-width:200px">
                                    </div>
                                    <div class="col-lg row">
                                        <div class="row">
                                            <span>Book: <RouterLink :to="'/book/'+non_rate.book_id">
                                                    {{non_rate.book_name}}
                                                </RouterLink></span>
                                        </div>
                                        <div class="row"><span>Section: {{non_rate.section_name}}</span></div>
                                        <div class="row"><span>Author: {{non_rate.author_name}}</span></div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div :id="'collapsenon'+non_rate.book_id" class="accordion-collapse collapse"
                        data-bs-parent="#nonratedlist">
                        <div class="accordion-body">
                            <Ratinggive :rating="non_rate">
                            </Ratinggive>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
