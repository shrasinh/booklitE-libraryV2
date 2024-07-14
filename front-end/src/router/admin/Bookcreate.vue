<script setup>
    import { useLoadingStore, useBookcreateStore } from '../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string, number, mixed } from "yup"
    import { useRouter } from 'vue-router'
    import { onMounted } from 'vue'

    const router = useRouter()
    onMounted( async () =>
    {
        if ( Object.keys( useBookcreateStore().languages ).length == 0 )
        {
            useLoadingStore().loading = true
            let r = await fetchfunct( backurl + "admin/books" )
            if ( r.ok )
            {
                r = await r.json()
                useBookcreateStore().sections = r.sections
                useBookcreateStore().languages = r.languages
            }
            else
            {
                checkerror( r )
            }
            // stopping the loading screen
            useLoadingStore().loading = false
        }
    } )

    const validFileExtensions = {
        image: [ 'jpg', 'png', 'jpeg' ],
        pdf: [ 'pdf' ]
    }

    function isValidFileType ( fileName, fileType )
    {
        return fileName && validFileExtensions[ fileType ].indexOf( fileName.split( '.' ).pop() ) > -1;
    }

    const book_schema = object().shape( {
        book_name: string().required(),
        book_description: string().required(),
        author_name: string().required(),
        price: number().typeError( "Not a valid number" ).min( 0 ).required().test( "is-less-than-3-decimals",
            "Enter the price value with lesser than 3 decimal precision", value =>
        {
            if ( ( value % 1 ) != 0 )
                return value.toString().split( "." )[ 1 ].length < 3
            return true // for integers
        }
        ),
        no_of_copies_available: number().typeError( "Not a valid number" ).integer().min( 0 ).required(),
        section_id: number().required().test( "is-valid", "Enter a valid choice for section", value =>
            !!useBookcreateStore().sections.filter( e => e.section_id == value )
        ),
        language: string().required().test( "is-valid", "Enter a valid choice for language", value =>
            !!useBookcreateStore().languages[ value ]
        ),
        thumbnail: mixed().required().test( "is-valid-type", "Jpg, png, jpeg file only",
            value => isValidFileType( value && value.name.toLowerCase(), "image" ) ),
        book_pdf: mixed().required().test( "is-valid-type", "Pdf file only",
            value => isValidFileType( value && value.name.toLowerCase(), "pdf" ) ),
    } )

    async function submit ( values )
    {
        useLoadingStore().loading = true

        let bodyContent = new FormData()

        bodyContent.append(
            "name", values.book_name,
        )
        bodyContent.append(
            "content", values.book_description,
        )
        bodyContent.append(
            "author", values.author_name,
        )
        bodyContent.append(
            "price", values.price,
        )
        bodyContent.append(
            "language", values.language,
        )
        bodyContent.append(
            "section_id", values.section_id,
        )
        bodyContent.append(
            "thumbnail", values.thumbnail
        )
        bodyContent.append(
            "storage", values.book_pdf
        )
        bodyContent.append(
            "noofcopies", values.no_of_copies_available,
        )

        let r = await fetchfunct( backurl + "admin/books/create", {
            method: "POST", body: bodyContent
        } )
        if ( r.ok )
        {
            router.push( '/admin/books' )
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
    <h1 class="mb-3 p-2">Book Addition</h1>
    <Form :validation-schema="book_schema" @submit="submit">

        <div class="row mb-lg-3 mx-auto">
            <div class="col-lg-5 me-lg-auto">
                <div class="row">
                    <label class="form-label">Book name</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class='form-control' name="book_name" placeholder='Book name'></Field>
                    <ErrorMessage class="form-text" name="book_name"></ErrorMessage>
                </div>
            </div>
            <div class="col-lg-5 ms-lg-auto">
                <div class="row">
                    <label class="form-label">Author name</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class='form-control' name="author_name" placeholder='Author name'></Field>
                    <ErrorMessage class="form-text" name="author_name"></ErrorMessage>
                </div>
            </div>
        </div>

        <div class="row mb-lg-3 mx-auto">
            <div class="col-lg-5 me-lg-auto">
                <div class="row">
                    <label class="form-label">Book price(in Rs.)</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class='form-control' name="price" placeholder='Book price' type="number" min="0"></Field>
                    <ErrorMessage class="form-text" name="price"></ErrorMessage>
                </div>
            </div>
            <div class="col-lg-5 ms-lg-auto">
                <div class="row">
                    <label class="form-label">Number of Copies Available</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class='form-control' name="no_of_copies_available" placeholder='Number of copies'
                        type="number" min="0">
                    </Field>
                    <ErrorMessage class="form-text" name="no_of_copies_available"></ErrorMessage>
                </div>
            </div>
        </div>

        <div class="row mb-lg-3 mx-auto">
            <div class="col-lg-5 me-lg-auto">
                <div class="row">
                    <label class="form-label">Associated Section</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class="form-select" name="section_id" as="select">
                        <option value="" disabled>Select a section</option>
                        <option v-for="section in useBookcreateStore().sections" :key="section.section_id"
                            :value="section.section_id">
                            {{ section.section_name }}
                        </option>
                    </Field>
                    <ErrorMessage class="form-text" name="section_id"></ErrorMessage>
                </div>
            </div>
            <div class="col-lg-5 ms-lg-auto">
                <div class="row">
                    <label class="form-label">Language</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class="form-select" name="language" as="select">
                        <option value="" disabled>Select language</option>
                        <option v-for="(language_id,language_name) in useBookcreateStore().languages" :key="language_id"
                            :value="language_name">
                            {{ language_name }}
                        </option>
                    </Field>
                    <ErrorMessage class="form-text" name="language"></ErrorMessage>
                </div>
            </div>
        </div>

        <div class="row mb-lg-3 mx-auto">
            <div class="col-lg-5 me-lg-auto">
                <div class="row">
                    <label class="form-label">Book description</label>
                </div>
                <div class="row form-element mx-auto mb-3 mb-lg-0">
                    <Field class='form-control' name="book_description" placeholder='Book description' as="Textarea"
                        cols="30" rows="10"></Field>
                    <ErrorMessage class="form-text" name="book_description"></ErrorMessage>
                </div>
            </div>
            <div class="col-lg-5 ms-lg-auto">
                <div class="row mb-lg-3">
                    <div class="row">
                        <label class="form-label">Book pdf</label>
                    </div>
                    <div class="row form-element mx-auto mb-3 mb-lg-0">
                        <Field name="book_pdf" class='form-control' type="file" accept="application/pdf">
                        </Field>
                        <ErrorMessage class="form-text" name="book_pdf"></ErrorMessage>
                    </div>
                </div>
                <div class="row mb-lg-3">
                    <div class="row ">
                        <label class="form-label">Book thumbnail</label>
                    </div>
                    <div class="row form-element mx-auto mb-3 mb-lg-0">
                        <Field name="thumbnail" class='form-control' type="file"
                            accept="image/png, image/jpg, image/jpeg">
                        </Field>
                        <ErrorMessage class="form-text" name="thumbnail"></ErrorMessage>
                    </div>
                </div>
            </div>
        </div>

        <div class='row mb-3'>
            <div class="col-auto mx-lg-auto ms-3">
                <button type="submit" class='btn btn-outline-primary'>Submit</button>
            </div>
        </div>
    </Form>
</template>