<script setup>
    import { useLoadingStore } from '../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string } from "yup"
    import { useRouter } from 'vue-router'

    const router = useRouter()

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

        let r = await fetchfunct( backurl + "admin/sections/create", {
            method: "POST", body: bodyContent
        } )
        if ( r.ok )
        {
            router.push( '/admin/sections' )
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
    <h1 class="mb-3 p-2">Section Addition</h1>
    <br>
    <Form :validation-schema="section_schema" @submit="submit">
        <div class='row mb-3 form-element mx-auto'>
            <div class="col-lg-2">
                <label class="form-label">Section name</label>
            </div>
            <div class="col-auto">
                <Field class='form-control' name="section_name" placeholder='section name'></Field>
                <ErrorMessage class="form-text" name="section_name"></ErrorMessage>
            </div>
        </div>
        <div class='row mb-3 form-element mx-auto'>
            <div class="col-lg-2">
                <label class="form-label">Section description</label>
            </div>
            <div class="col-auto">
                <Field class='form-control' name="section_description" placeholder='section description' as="Textarea"
                    cols="100" rows="10"></Field>
                <ErrorMessage class="form-text" name="section_description"></ErrorMessage>
            </div>
        </div>
        <div class='row mb-3 mx-auto'>
            <div class="col-auto offset-md-2">
                <button type="submit" class='btn btn-outline-primary'>Submit</button>
            </div>
        </div>
    </Form>
</template>
