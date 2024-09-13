<script setup>
    import { ref, computed } from 'vue'
    import { fetchfunct, checkerror, checksuccess } from '../../components/fetch.js'
    import Bookview from '../../components/Bookview.vue'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { useLoadingStore, useBookcreateStore, useBookdetailsStore } from '../../stores/store.js'
    import { object, string, number } from "yup"

    const props = defineProps( [ 'book' ] )
    const book = ref( { ...props.book } )
    const editing = ref( false )

    const section_name = computed( () =>
    {
        {
            const s = useBookcreateStore().sections.find( e => e.section_id == book.value.section.section_id )
            if ( s )
                return s.section_name
        }
    } )

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
        } ),
        no_of_copies_available: number().typeError( "Not a valid number" ).integer().min( 0 ).required(),
        section_id: number().required().test( "is-valid", "Enter a valid choice for section", value =>
            !!useBookcreateStore().sections.find( e => e.section_id == value )
        ),
        language: string().required().test( "is-valid", "Enter a valid choice for language", value =>
            !!useBookcreateStore().languages[ value ]
        )
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
            "noofcopies", values.no_of_copies_available,
        )

        let r = await fetchfunct( backurl + `admin/books/edit/${ book.value.book_id }`, {
            method: "PUT", body: bodyContent,
        } )
        if ( r.ok )
        {
            editing.value = false

            for ( const i in useBookdetailsStore().books )
            {
                if ( useBookdetailsStore().books[ i ].book_id == book.value.book_id )
                {
                    useBookdetailsStore().books[ i ] = { ...book.value }
                }
                break
            }

            Object.assign( props.book, book.value ); //changing the parent data

            checksuccess( r )
        }
        else
        {
            Object.assign( book.value, props.book );// resetting the child data to the original data
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } 
</script>

<template>
    <h4 class="mb-3">Book Details <i @click="editing=!editing" title="Edit the book details"
            class="bi bi-pencil-square pointer-link" :style="(!editing)&&{'color':'gray'}"></i>
    </h4>
    <div class="row mb-3">
        <div class="col-md">Currently issued by</div>
        <div v-if="book.currently_issued_by.length==0" class="col text-muted">The books is not currently issued by
            anyone.</div>
        <div v-else class="col-md">
            <table class="table table-bordered text-center table-responsive">
                <thead>
                    <tr>
                        <th scope="col-md">Username</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in book.currently_issued_by" class="col">
                        <td>{{user.username}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div class="row mb-3">
        <div class="col-md">Book view</div>
        <div class="col-md">
            <Bookview :language="useBookcreateStore().languages[book.language ]" :url="book.book_storage"
                :book_name="book.book_name" :icon="false" :id="'book'+book.book_id"></Bookview>
        </div>
    </div>
    <Form :validation-schema="book_schema" @submit="submit">
        <div class="row mb-3 form-element">
            <div class="col-md">Name</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.book_name" class='form-control' name="book_name" placeholder='book name'></Field>
                <ErrorMessage class="form-text" name="book_name"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{book.book_name}}</div>
        </div>


        <div class="row mb-3 form-element">
            <div class="col-md-6">Description</div>
            <div class="col-md-6" v-if="editing">
                <Field v-model="book.description" class='form-control' name="book_description"
                    placeholder='Book description' as="Textarea" cols="30" rows="10"></Field>
                <ErrorMessage class="form-text" name="book_description"></ErrorMessage>
            </div>
            <div v-else class="col-md-6 break-word">{{book.description}}</div>
        </div>

        <div class="row mb-3 form-element">
            <div class="col-md">Author name</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.author" class='form-control' name="author_name" placeholder='Author name'>
                </Field>
                <ErrorMessage class="form-text" name="author_name"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{book.author}}</div>
        </div>

        <div class="row mb-3 form-element">
            <div class="col-md">Price(in Rs.)</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.price" class='form-control' name="price" placeholder='Book price' type="number"
                    min="0"></Field>
                <ErrorMessage class="form-text" name="price"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{book.price }}</div>
        </div>
        <div class="row mb-3 form-element">
            <div class="col-md">Number of Books Available</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.no_of_copies_available" class='form-control' name="no_of_copies_available"
                    placeholder='Number of copies' type="number" min="0">
                </Field>
                <ErrorMessage class="form-text" name="no_of_copies_available"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{book.no_of_copies_available}}</div>
        </div>
        <div class="row mb-3 form-element">
            <div class="col-md">Associated Section</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.section.section_id" class="form-select" name="section_id" as="select">
                    <option value="" disabled>Select a section</option>
                    <option v-for="section in useBookcreateStore().sections" :key="section.section_id"
                        :value="section.section_id">
                        {{ section.section_name }}
                    </option>
                </Field>
                <ErrorMessage class="form-text" name="section_id"></ErrorMessage>
            </div>
            <div v-else class="col-md">{{section_name}}</div>
        </div>
        <div class="row mb-3 form-element">
            <div class="col-md">Language</div>
            <div class="col-md" v-if="editing">
                <Field v-model="book.language" class="form-select" name="language" as="select">
                    <option value="" disabled>Select language</option>
                    <option v-for="(language_id,language_name) in useBookcreateStore().languages" :key="language_id"
                        :value="language_name">
                        {{ language_name }}
                    </option>
                </Field>
            </div>
            <div v-else class="col-md">{{book.language}}</div>
        </div>

        <div class='row mb-3'>
            <div class="col offset-md-6">
                <button v-show="editing" type="submit" class='btn btn-outline-success'>Submit</button>
            </div>
        </div>
    </Form>
</template>