<script setup>
    defineProps( [ 'rating' ] )
</script>
<template>
    <div class="Stars" :style="{'--rating': rating}" :title="!rating?'Not rated yet':rating+' stars'"></div>
</template>
<style scoped>
    .Stars {
        --percent: calc(var(--rating) / 5 * 100%);

        display: inline-block;
        font-size: var(--star-size);
        font-family: Times;
        line-height: 1;

        &::before {
            content: '★★★★★';
            letter-spacing: 3px;
            background: linear-gradient(90deg, var(--star-background) var(--percent), var(--star-color) var(--percent));
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    }
</style>
