<script setup>
    import { onMounted, ref } from 'vue'
    import Animationinteger from '../../../components/Animationinteger.vue'

    const props = defineProps( [ 'admin' ] )
    const admin = ref( props.admin )

    function draw ()
    {
        var data = google.visualization.arrayToDataTable( [
            [ 'User Type', 'User Count' ],
            ...admin.value.graph
        ] )

        var options = {
            backgroundColor: 'none',
            title: 'User count breakdown',
            hAxis: {
                title: 'User Type',
            },
            vAxis: {
                title: 'User Count',
                viewWindowMode: 'maximized'
            },
            animation: {
                startup: true,
                duration: 1000,
                easing: 'inAndOut'
            },
            tooltip: { isHtml: true }
        };

        var chart = new google.visualization.ColumnChart( document.getElementById( 'admin_chart' ) );

        chart.draw( data, options );
    }

    onMounted( () =>
    {
        window.google.charts.load( 'current', {
            packages: [ 'corechart', 'bar' ]
        } );
        window.google.charts.setOnLoadCallback( draw );
        window.onresize = draw;
    } )

</script>
<template>
    <div class="text-center">
        <h1>Library Stats</h1>
        <br>
        <div class="row">
            <div class="col mb-3">
                <h5>Number of Users registered<br>
                    <Animationinteger :value="admin.user_count"></Animationinteger>
                </h5>
            </div>
            <div class="col mb-3">
                <h5>Number of Sections present<br>
                    <Animationinteger :value="admin.section_count"></Animationinteger>
                </h5>
            </div>
        </div>
        <div class="row">
            <div class="col mb-3 mt-5">
                <h5>Number of Books present<br>
                    <Animationinteger :value="admin.book_count"></Animationinteger>
                </h5>
            </div>
            <div class="col mb-3 mt-5">
                <h5>Number of Times Books issued<br>
                    <Animationinteger :value="admin.issued_book_count"></Animationinteger>
                </h5>
            </div>
            <div class="col-lg row text-center mb-3 mt-5">
                <h5>Number of Books purchased<br>
                    <Animationinteger :value="admin.purchased_book_count"></Animationinteger>
                </h5>
            </div>
        </div>
        <div class="row justify-content-center">
            <div class="col-auto" id="admin_chart" style="width:60%;min-height: 400px;"></div>
        </div>
    </div>
</template>