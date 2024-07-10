<script setup>
    import { ref, computed } from 'vue'
    const rate = ref( 0 )
    const title = computed( () =>
    {
        if ( rate.value == '5' )
        {
            return "Very good!"
        }
        else if ( rate.value == '4' )
        {
            return "Good!"
        }
        else if ( rate.value == '3' )
        {
            return "Average"
        }
        else if ( rate.value == '2' )
        {
            return "Poor"
        }
        else 
        {
            return "Very poor!"
        }

    } )
</script>
<template>
    <div class="rate">
        <input type="radio" v-model="rate" value="5" />
        <label title="Very good">5 stars</label>
        <input type="radio" v-model="rate" value="4" />
        <label title="Good">4 stars</label>
        <input type="radio" v-model="rate" value="3" />
        <label title="Average">3 stars</label>
        <input type="radio" v-model="rate" value="2" />
        <label title="Poor">2 stars</label>
        <input type="radio" v-model="rate" value="1" />
        <label title="Very poor">1 star</label>
    </div> {{ title }}
</template>
<style scoped>
    * {
        margin: 0;
        padding: 0;
    }

    .rate {
        float: left;
        height: 46px;
        padding: 0 10px;
    }

    .rate:not(:checked)>input {
        position: absolute;
        top: -9999px;
    }

    .rate:not(:checked)>label {
        float: right;
        width: 1em;
        overflow: hidden;
        white-space: nowrap;
        cursor: pointer;
        font-size: 30px;
        color: #ccc;
    }

    .rate:not(:checked)>label:before {
        content: '★ ';
    }

    .rate>input:checked~label {
        color: #ffc700;
    }

    .rate:not(:checked)>label:hover,
    .rate:not(:checked)>label:hover~label {
        color: #deb217;
    }

    .rate>input:checked+label:hover,
    .rate>input:checked+label:hover~label,
    .rate>input:checked~label:hover,
    .rate>input:checked~label:hover~label,
    .rate>label:hover~input:checked~label {
        color: #c59b08;
    }
</style>