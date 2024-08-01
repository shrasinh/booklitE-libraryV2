<script setup>
    import { onMounted, ref } from 'vue';
    const installPrompt = ref( null )
    function toast_display ( event )
    {
        event.preventDefault();
        installPrompt.value = event
        bootstrap.Toast.getOrCreateInstance( document.getElementById( 'install-prompt' ), { delay: 10000 } ).show()
    }

    onMounted( () =>
    {
        window.addEventListener( "beforeinstallprompt", toast_display )

    } )

    function install ()
    {
        bootstrap.Toast.getInstance( document.getElementById( 'install-prompt' ) ).dispose()
        window.removeEventListener( "beforeinstallprompt", toast_display )

        if ( !installPrompt.value )
        {
            return;
        }
        installPrompt.value.prompt()

    }
</script>
<template>

    <div class="toast-container start-50 translate-middle" style="padding-top: 12rem">
        <div id="install-prompt" class="toast">
            <div class="toast-header">
                <img src="https://img.icons8.com/color/92/story-book.png" class="rounded me-2">
                <strong class="me-auto">Install Booklit</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                <p>To enjoy a better experience install Booklit on your home screen.</p>
                <p>Just tap on the "Confirm" button and then "Install".</p>
                <div class="mt-2 pt-2 border-top text-center">
                    <button type="button" class="btn btn-success btn-sm me-2" @click="install">Confirm</button>
                    <button type="button" class="btn btn-danger btn-sm ms-2" data-bs-dismiss="toast">Close</button>
                </div>
            </div>

        </div>
    </div>
    <div class="toast-container position-fixed bottom-0 end-0">
        <div id="export-notification" class="toast">
            <div class="toast-header">
                <img src="https://img.icons8.com/color/92/story-book.png" class="rounded me-2">
                <strong class="me-auto">Booklit</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
            </div>
        </div>
    </div>
</template>