<script setup>
    import { ref } from 'vue'
    import { useLoadingStore } from '../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string } from "yup"

    const props = defineProps( [ 'section' ] )
    const section = ref( props.section )
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
            method: "PUT", body: bodyContent,
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {
            editing.value = false
            checksuccess( r )
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
    <h4 class="mb-3">Section Details <i @click="editing=!editing" title="Edit the section details"
            class="bi bi-pencil-square pointer-link" :style="(!editing)&&{'color':'gray'}"></i>
    </h4>
    <div class="row mb-3">
        <div class="col">Books present</div>
        <div v-if="section.books.length==0" class="col text-muted">No books are currently
            present in
            the section.</div>
        <div v-else class="col">
            <table class="table table-bordered text-center">
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
            <div class="col">Name</div>
            <div class="col" v-if="editing">
                <Field v-model="section.section_name" class='form-control' name="section_name"
                    placeholder='section name'></Field>
                <ErrorMessage class="form-text" name="section_name"></ErrorMessage>
            </div>
            <div v-else class="col">{{section.section_name}}</div>
        </div>


        <div class="row mb-3 form-element">
            <div class="col">Description</div>
            <div class="col" v-if="editing">
                <Field v-model="section.description" class='form-control' name="section_description"
                    placeholder='section description' as="Textarea" cols="100" rows="10"></Field>
                <ErrorMessage class="form-text" name="section_description"></ErrorMessage>
            </div>
            <div v-else class="col">{{section.description}}</div>
        </div>
        <div class='row mb-3'>
            <div class="col offset-md-6">
                <button v-show="editing" type="submit" class='btn btn-outline-success'>Submit</button>
            </div>
        </div>

    </Form>



</template>