<script setup>
    import { ref, onMounted } from 'vue'


    const props = defineProps( { value: Number } )
    const tweeningValue = ref( 0 )

    onMounted( () =>
    {
        function animate ()
        {
            if ( window.TWEEN.update() )
            {
                requestAnimationFrame( animate )
            }
        }
        new window.TWEEN.Tween( {
            tweeningValue: 0
        } )
            .to( {
                tweeningValue: props.value
            }, 1000 )
            .onUpdate( function ()
            {
                tweeningValue.value = this.tweeningValue.toFixed( 0 )
            } )
            .start()
        animate()

    } )
</script>

<template>
    <span>{{ tweeningValue }}</span>
</template>