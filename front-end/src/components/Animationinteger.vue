<script setup>
    import { onBeforeMount, ref, watch } from 'vue'

    onBeforeMount( () =>
    {
        if ( !document.getElementById( 'tweenscript' ) )
        {
            let tween_script = document.createElement( 'script' )
            tween_script.src = "https://cdn.jsdelivr.net/npm/tween.js"
            tween_script.async = false
            tween_script.id = "tweenscript"
            document.head.appendChild( tween_script )
        }
    } )

    const props = defineProps( { value: Number } )
    const tweeningValue = ref( 0 )
    watch( () => props.value, ( newvalue, oldvalue ) =>
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
                tweeningValue: newvalue
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