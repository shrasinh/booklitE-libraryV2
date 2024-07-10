<script setup>
    import { onMounted, reactive, onBeforeMount } from 'vue'
    import { useLoadingStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import Animationinteger from '../../components/Animationinteger.vue'

    const details = reactive( {
        graph: [ [ "Normal users", 0 ], [ "Members", 0 ] ],
        user_count: 0,
        section_count: 0,
        book_count: 0,
        purchased_book_count: 0,
        issued_book_count: 0,
    } )

    onBeforeMount( () =>
    {
        if ( !document.getElementById( 'chartscript' ) )
        {
            let chart_script = document.createElement( 'script' )
            chart_script.src = "https://www.gstatic.com/charts/loader.js"
            chart_script.async = false
            chart_script.id = "chartscript"
            document.head.appendChild( chart_script )

        }
    } )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/dashboard", {
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {
            r = await r.json()
            details.graph = r.graph
            details.book_count = r.book_count
            details.user_count = r.user_count
            details.section_count = r.section_count
            details.purchased_book_count = r.purchased_book_count
            details.issued_book_count = r.issued_book_count
        }
        else
        {
            checkerror( r )
        }

        window.google.charts.load( 'current', {
            packages: [ 'corechart', 'bar' ]
        } );
        window.google.charts.setOnLoadCallback( draw );

        function draw ()
        {

            var data = google.visualization.arrayToDataTable( [
                [ 'User Type', 'User Count' ],
                ...details.graph
            ] )

            var options = {
                width: 600,
                height: 400,
                title: 'User count breakdown',
                hAxis: {
                    title: 'User Type',
                },
                vAxis: {
                    title: 'User Count',
                    viewWindowMode: "maximized"
                }
            };

            var chart = new google.visualization.ColumnChart( document.getElementById( 'admin_chart' ) );

            chart.draw( data, options );
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

</script>
<template>
    <div class="text-center">
        <h1>Library Stats</h1>
        <br>
        <div class="row mb-3">
            <div class="col">
                <h5>Number of Users registered<br>
                    <Animationinteger :value="details.user_count"></Animationinteger>
                </h5>
            </div>
            <div class="col">
                <h5>Number of Sections present<br>
                    <Animationinteger :value="details.section_count"></Animationinteger>
                </h5>
            </div>
        </div>
        <div class="row mb-3"></div>
        <div class="row mb-3">
            <div class="col">
                <h5>Number of Books present<br>
                    <Animationinteger :value="details.book_count"></Animationinteger>
                </h5>
            </div>
            <div class="col">
                <h5>Number of Times Books issued<br>
                    <Animationinteger :value="details.issued_book_count"></Animationinteger>
                </h5>
            </div>
            <div class="col">
                <h5>Number of Books purchased<br>
                    <Animationinteger :value="details.purchased_book_count"></Animationinteger>
                </h5>
            </div>
        </div>
        <div class="d-flex justify-content-center" id="admin_chart"></div>
    </div>
</template>