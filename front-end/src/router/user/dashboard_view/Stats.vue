<script setup>
    import { onMounted, ref } from 'vue'
    import Animationinteger from '../../../components/Animationinteger.vue'

    const props = defineProps( [ 'user' ] )
    const user = ref( props.user )

    function draw ()
    {
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn( { type: 'string', id: 'Book name' } );
        dataTable.addColumn( { type: 'date', id: 'Issue date' } );
        dataTable.addColumn( { type: 'date', id: 'Return date' } );
        dataTable.addRows( [ ...user.value.graph ] );

        var chart = new google.visualization.Timeline( document.getElementById( 'user_chart' ) );
        chart.draw( dataTable );
    }

    onMounted( () =>
    {
        if ( user.value.graph.length > 0 )
        {
            for ( const i in user.value.graph )
            {
                user.value.graph[ i ][ 1 ] = new Date( user.value.graph[ i ][ 1 ] )
                user.value.graph[ i ][ 2 ] = new Date( user.value.graph[ i ][ 2 ] )

            }
            window.google.charts.load( 'current', { 'packages': [ 'timeline' ] } );
            window.google.charts.setOnLoadCallback( draw );
            window.onresize = draw
        }
    } )

</script>

<template>
    <div class="text-center p-4">
        <h1>Usage Stats</h1>
        <br>
        <div class="h-100 d-flex flex-column">
            <div class="row h-50">
                <div class="row mb-3">
                    <div class="col">
                        <h5>Number of Times Books issued<br>
                            <Animationinteger :value="user.issued_book_count"></Animationinteger>
                        </h5>
                    </div>
                    <div class="col">
                        <h5>Number of Books purchased<br>
                            <Animationinteger :value="user.purchased_book_count"></Animationinteger>
                        </h5>
                    </div>
                </div>
                <div class="row mb-3 mt-5">
                    <div class="col">
                        <h5>Number of times Logged in<br>
                            <Animationinteger :value="user.login_count"></Animationinteger>
                        </h5>
                    </div>
                    <div class="col">
                        <h5>Number of Ratings given<br>
                            <Animationinteger :value="user.rating_count"></Animationinteger>
                        </h5>
                    </div>
                </div>
            </div>

            <div class="row mt-5 justify-content-center">
                <h5 class="mb-3">Timeline for current issue</h5>
                <div v-if="user.graph.length==0" class="text-muted">No books are currently issued</div>
                <div v-else id="user_chart"></div>
            </div>

        </div>
    </div>
</template>
<style scoped>
    #user_chart {
        max-width: 80%;
    }
</style>