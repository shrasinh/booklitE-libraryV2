<script setup>
    import { ref } from 'vue'
    import { useLoadingStore, useBookcreateStore } from '../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string } from "yup"

    const props = defineProps( [ 'section' ] )
    const original = ref( props.section )
    const section = ref( { ...original.value } )
    const editing = ref( false )

    const section_schema = object().shape( {
        section_name: string().required().strict(),
        section_description: string().required().strict(),
    } )

    async function submit ( values )
    {
        useLoadingStore().loading = true

        let bodyContent = new FormData()

        bodyContent.append(
            "name", values.section_name,
        )
        bodyContent.append(
            "description", values.section_description,

        )

        let r = await fetchfunct( backurl + `admin/sections/edit/${ section.value.section_id }`, {
            method: "PUT", body: bodyContent
        } )
        if ( r.ok )
        {
            editing.value = false
            for ( const i in useBookcreateStore().sections )
            {
                if ( useBookcreateStore().sections[ i ].section_id == section.value.section_id )
                {
                    useBookcreateStore().sections[ i ] = { ...section.value }
                }
                break
            }
            original.value = { ...section.value }// changing the parent data
            checksuccess( r )
        }
        else
        {
            checkerror( r )
            section.value = { ...original.value } // resetting the child data to the original data
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } 
</script>
<template>
    <h4 class="mb-3">Section Details <i @click="editing=!editing" title="Edit the section details"
            class="bi bi-pencil-square pointer-link" :style="(!editing)&&{'color':'gray'}"></i>
    </h4>
    <div class="row mb-3">
        <div class="col-md">Books present</div>
        <div v-if="section.books.length==0" class="col text-muted">No books are currently
            present in
            the section.</div>
        <div v-else class="col-md">
            <table class="table table-bordered table-responsive text-center">
                <thead>
                    <tr>
                        <th scope="col">Book name</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="book in section.books" class="col">
                        <td>{{book.book_name}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <Form :validation-schema="section_schema" @submit="submit">
        <div class="row mb-3 form-element">
            <div class="col-md">Name</div>
            <div class="col-md" v-if="editing">
                <Field v-model="section.section_name" class='form-control' name="section_name"
                    placeholder='section name'></Field>
                <ErrorMessage class="form-text" name="section_name"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{section.section_name}}</div>
        </div>


        <div class="row mb-3 form-element">
            <div class="col-md">Description</div>
            <div class="col-md" v-if="editing">
                <Field v-model="section.description" class='form-control' name="section_description"
                    placeholder='section description' as="Textarea" cols="100" rows="10"></Field>
                <ErrorMessage class="form-text" name="section_description"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{section.description}}</div>
        </div>
        <div class='row mb-3'>
            <div class="col offset-md-6">
                <button v-show="editing" type="submit" class='btn btn-outline-success'>Submit</button>
            </div>
        </div>

    </Form>



</template>