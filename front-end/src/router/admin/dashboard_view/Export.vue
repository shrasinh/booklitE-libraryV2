<script setup>
    import { ref } from 'vue';
    import { useLoadingStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror } from '../../../components/fetch.js'
    const etype = ref( "section" )

    async function export_details ()
    {
        const targetContainer = document.querySelector( "#export-notification .toast-body" ); // present in Toast vue in components folder
        const button = document.querySelector( "#export-button" );
        button.setAttribute( "disabled", true );

        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/export?etype=" + etype.value )
        if ( r.ok )
        {
            r = await r.json()
            let task_id = r.task_id
            targetContainer.textContent = `Starting to export...`
            bootstrap.Toast.getOrCreateInstance( document.getElementById( 'export-notification' ) ).show()

            let eventSource = new EventSource( `${ backurl }/admin/export/notify/${ task_id }?auth_token=${ localStorage.getItem(
                "Authentication-Token" ) }` )

            eventSource.onerror = function ()
            {
                targetContainer.textContent = "Export has failed. Try again later!"
                eventSource.close();
                bootstrap.Toast.getOrCreateInstance( document.getElementById( 'export-notification' ) ).show()
            };

            eventSource.onmessage = async function ( e )
            {
                targetContainer.textContent = `Export is successfully completed!`;
                eventSource.close();
                bootstrap.Toast.getOrCreateInstance( document.getElementById( 'export-notification' ) ).show()

                const pdfData = e.data;
                const pdfBlob = new Blob( [ Uint8Array.from( atob( pdfData ), c => c.charCodeAt( 0 ) ) ], { type: 'application/pdf' } );
                const pdfUrl = URL.createObjectURL( pdfBlob ); //assign a url to the blob object that can used by anchor tag to download the content
                const anchor = document.createElement( "a" )
                anchor.href = pdfUrl
                anchor.download = `export_details_${ new Date().toLocaleString() }.csv`
                document.body.appendChild( anchor )
                anchor.click()
                document.body.removeChild( anchor )
                URL.revokeObjectURL( pdfUrl )
            };
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        button.removeAttribute( "disabled" );
        useLoadingStore().loading = false
    }
</script>
<template>
    <div class="text-center">
        <h1>Export library details</h1>
        <div class="row mb-3 mt-5 justify-content-center">
            <div class="col-auto">Select export details' type</div>
            <div class="col-auto">
                <select class="form-select" v-model="etype">
                    <option :value="'section'">Sections</option>
                    <option :value="'book'">Books</option>
                    <option :value="'user'">Users</option>
                </select>
            </div>
            <div class="col-auto">
                <button class="btn btn-outline-success" id="export-button" @click="export_details">Export</button>
            </div>
        </div>
    </div>
</template>