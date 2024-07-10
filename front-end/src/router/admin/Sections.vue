<script setup>
    import { onMounted, ref, h } from 'vue'
    import { RouterLink } from 'vue-router'
    import { useAlertStore, useLoadingStore, useModalStore, useBookcreateStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import Sectionedit from './Sectionedit.vue'

    const sections = ref( [] )
    const search = ref( "" )
    const checked = ref( [] )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/sections", {
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {
            r = await r.json()
            sections.value = r.sections
            useBookcreateStore().sections = r.sections
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

    function deletesectionchecking ()
    {
        if ( checked.value.length != 0 )
        {
            const deletesectionModal = {
                id: 'deletesectionModal',
                title: 'Section delete confirmation',
                body: h( 'div', [ h( 'p', 'Are you sure you want to delete the following sections along with any books and data associated with them?' ),
                h( 'ul', checked.value.map( ( id => h( 'li', `Section ID: ${ id }` ) ) ) ) ] ),
                footer: h( 'button', { class: 'btn btn-danger', onClick: () => deletesection() }, 'Confirm' )
            }

            useModalStore().modalfunc( deletesectionModal )

        }

    }

    async function deletesection ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()

        useLoadingStore().loading = true
        let bodyContent = new FormData()

        bodyContent.append(
            "section_ids", checked.value,
        )
        let r = await fetchfunct( backurl + "admin/sections/delete", {
            method: "DELETE", body: bodyContent,
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {   //removing the deleted section and resetting the checked array
            sections.value = sections.value.filter( s => !checked.value.includes( s.section_id ) )
            checked.value.length = 0

            //providing feedback
            r = await r.json()
            if ( r.response.errors.length == 0 )
            { useAlertStore().alertpush( [ { msg: 'Selected sections are successfully deleted!', type: 'alert-success' } ] ) }
            else
            { useAlertStore().alertpush( r.response.errors.map( e => { return { msg: e, type: 'alert-danger' } } ) ) }
        }
        else
        {
            checkerror( r )
        }

        // stopping the loading screen
        useLoadingStore().loading = false
    }

</script>

<template>

    <div class='row mb-3 justify-content-between align-items-center'>
        <div class="col-auto">
            <h1 class="mb-3 p-2">All sections</h1>
        </div>
        <div class="col-auto">
            <input class="form-control search-icon" placeholder="Search for a section..." v-model="search">
        </div>
    </div>

    <p v-if="sections.length===0" class="text-muted mb-3 p-2">
        No section added yet.</p>

    <div v-else>

        <div class="row mx-auto text-center">
            <div class="col-auto"><i @click="deletesectionchecking" title="Delete sections" class="bi bi-trash3"
                    :class="(checked.length!=0)&&'pointer-link'" :style="(checked.length==0)&&{'color':'gray'}"></i>
            </div>
            <div class="col row">
                <div class="col-1"><strong>Section Id</strong></div>
                <div class="col-4"><strong>Section Name</strong></div>
                <div class="col"><strong>Date of creation</strong></div>
                <div class="col"><strong>Number of books</strong></div>
            </div>
        </div>

        <div class="accordion" id="sections">
            <div v-for="section in sections">
                <div class="accordion-item"
                    v-if="search.length==0|section.section_name.toLowerCase().includes(search.toLowerCase())">

                    <div class="accordion-header row align-items-center mx-auto">
                        <div class="col-auto"><input type="checkbox" :value="section.section_id" v-model="checked"
                                class="form-check-input" /></div>
                        <div class="accordion-button collapsed col row text-center" data-bs-toggle="collapse"
                            :data-bs-target="'#collapse'+section.section_id">
                            <div class="col-1">{{section.section_id}}</div>
                            <div class="col-4 break-word">{{section.section_name}}</div>
                            <div class="col">{{section.created_on}}</div>
                            <div class="col">{{section.books.length}}</div>
                        </div>
                    </div>

                    <div :id="'collapse'+section.section_id" class="accordion-collapse collapse"
                        data-bs-parent="#sections">
                        <div class="accordion-body">
                            <Sectionedit :section="section"></Sectionedit>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>

    <RouterLink id="sectioncreate" to="/admin/sections/create" style="z-index:3" class="position-fixed bottom-0 end-0">
        <button class="btn btn-primary rounded-pill" title="Create a new section"><i class="bi bi-plus-lg"></i></button>
    </RouterLink>

</template>
<style scoped>
    #sectioncreate button {
        position: relative;
        top: 0;
        transition: top ease 0.5s;
        font-size: 35px;
    }

    #sectioncreate:hover button {
        top: -5px;
    }

</style>
