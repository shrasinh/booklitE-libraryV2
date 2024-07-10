<script setup>
    import { onBeforeMount, onMounted, ref } from 'vue'
    import lottieWeb from 'https://cdn.skypack.dev/lottie-web'

    const props = defineProps( [ 'language', 'url', 'book_name', 'class', 'id' ] )

    const next_state = ref( "start" )
    const animation = ref( null )
    const playIconContainer = ref( null )
    const newUtt = ref( null )

    //used to break the pdf text into smaller chunks such that speech synthesis on non-local voices can work
    function speechUtteranceChunker ( utt, settings, callback )
    {
        const chunkLength = settings && settings.chunkLength || 160;
        const pattRegex = new RegExp( '^.{' + Math.floor( chunkLength / 2 ) + ',' + chunkLength + '}[\.\!\?\,]{1}|^.{1,' + chunkLength + '}$|^.{1,' + chunkLength + '} ' );
        const txt = ( settings && settings.offset !== undefined ? utt.text.substring( settings.offset ) : utt.text );
        const chunkArr = txt.match( pattRegex );

        if ( chunkArr[ 0 ] !== undefined && chunkArr[ 0 ].length > 2 )
        {
            const chunk = chunkArr[ 0 ];
            newUtt.value = new SpeechSynthesisUtterance( chunk );

            for ( const x in utt )
            {
                if ( x !== 'text' )
                {
                    newUtt.value[ x ] = utt[ x ];
                }
            }
            newUtt.value.onend = function ()
            {
                settings.offset = settings.offset || 0;
                settings.offset += chunk.length - 1;
                speechUtteranceChunker( utt, settings, callback );
            }
            speechSynthesis.speak( newUtt.value )

        } else
        {
            callback();
        }
    }


    // to play the button animation and control the speech synthesis
    async function playanimation ()
    {
        if ( next_state.value === 'start' )
        {
            const utterance = new SpeechSynthesisUtterance( await extractText( props.url ) )
            utterance.voice = speechSynthesis.getVoices().find( e => e.lang == props.language ) || speechSynthesis.getVoices()[ 0 ]
            utterance.lang = props.language

            animation.value.playSegments( [ 14, 27 ], true );
            next_state.value = 'pause'

            speechUtteranceChunker( utterance, { chunkLength: 120 }, function ()
            {
                animation.value.playSegments( [ 0, 14 ], true )
                next_state.value = 'start'
            } )

        } else if ( next_state.value == 'play' )
        {
            animation.value.playSegments( [ 14, 27 ], true )
            next_state.value = 'pause'
            speechSynthesis.resume()
        } else
        {
            animation.value.playSegments( [ 0, 14 ], true )
            next_state.value = 'play'
            speechSynthesis.pause()
        }
    }


    // to view the pdf
    function viewFile ()
    {
        const previewConfig = {
            showDownloadPDF: false,
            showPrintPDF: false,
            embedMode: "LIGHT_BOX",

        }
        const adobeDCView = new AdobeDC.View( { clientId: import.meta.env.VITE_ADOBE_ID, divId: props.id } );

        adobeDCView.previewFile( {
            content: {
                location: {
                    url: props.url,
                    headers: [ {
                        key: "Authentication-Token", value: localStorage.getItem(
                            "Authentication-Token" )
                    } ]
                }
            },
            metaData: { fileName: props.book_name }
        }, previewConfig )
    }


    // extract the text from the pdf
    function extractText ( pdfUrl )
    {
        const { pdfjsLib } = globalThis;
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.mjs';
        const pdf = pdfjsLib.getDocument( {
            url: pdfUrl,
            httpHeaders: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        return pdf.promise.then( function ( pdf )
        {
            var totalPageCount = pdf.numPages;
            var countPromises = [];
            for (
                var currentPage = 1;
                currentPage <= totalPageCount; currentPage++ )
            {
                var page = pdf.getPage( currentPage ); countPromises.push( page.then(
                    function ( page )
                    {
                        var textContent = page.getTextContent(); return textContent.then( function ( text )
                        {
                            return text.items.map( function ( s ) { return s.str; } ).join( '' );
                        } );
                    } ) );
            } return Promise.all( countPromises
            ).then( function ( texts ) { return texts.join( '' ); } );
        } );
    }

    onBeforeMount( () =>
    {
        // load the required scripts 
        if ( !document.getElementById( 'pdfviewscript' ) )
        {
            let script = document.createElement( 'script' )
            script.src = "https://documentservices.adobe.com/view-sdk/viewer.js"
            script.async = false
            script.id = "pdfviewscript"
            document.head.appendChild( script )

        }
        if ( !document.getElementById( 'pdfreaderscript' ) )
        {
            let script = document.createElement( 'script' )
            script.src = "https://mozilla.github.io/pdf.js/build/pdf.mjs"
            script.type = "module"
            script.async = false
            script.id = "pdfreaderscript"
            document.head.appendChild( script )
        }

    } )


    onMounted( () =>
    {

        speechSynthesis.getVoices()

        // for reset all the values when the pdf is closed
        const callback = ( mutationList, observer ) =>
        {
            for ( const mutation of mutationList )
            {
                if ( next_state.value != 'start' )
                {
                    animation.value.playSegments( [ 0, 14 ], true );
                    next_state.value = 'start'
                    speechSynthesis.cancel()
                    newUtt.value.removeEventListener( "end", newUtt.value.onend )
                }
            }
        }
        new MutationObserver( callback ).observe( document.getElementById( props.id ), { attributes: true } )

        // load the animation
        animation.value = lottieWeb.loadAnimation( {
            container: playIconContainer.value,
            path: 'https://maxst.icons8.com/vue-static/landings/animated-icons/icons/pause/pause.json', renderer: 'svg', loop:
                false, autoplay: false, name: "Play pause Animation",
        } )
        animation.value.goToAndStop( 14, true )
    } )


</script>

<template>
    <a :class='class' @click="viewFile">View book</a>
    <div class="adobe-dc-view" :id="id" style="position:absolute;z-index:2000;"></div>
    <div class="audio-player-container">
        <button class="play-icon" ref="playIconContainer" title="Listen to text to speech version of the pdf"
            @click="playanimation"></button>
    </div>
</template>

<style scoped>
    .audio-player-container {
        position: absolute;
        bottom: 2%;
        left: 2%;
        width: 50%;
        max-width: 80px;
        height: 80px;
        z-index: 2001;
        outline: 2px solid;
        display: none;
    }

    .play-icon {
        padding: 0;
        border: 0;
        background: inherit;
        cursor: pointer;
        outline: none;
        width: 40px;
        height: 40px;
        margin: 25% 25% 25% 25%;
    }

    .adobe-dc-view:has(iframe)+.audio-player-container {
        display: block;
    }
</style>