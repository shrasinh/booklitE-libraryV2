<script setup>
    import { ref, computed } from 'vue'
    import { storeToRefs } from 'pinia'
    import { useLoadingStore, useBookdetailsStore, useAlertStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'

    const props = defineProps( [ 'user' ] )
    const user = ref( props.user )
    const editing = ref( false )
    const issuecheck = ref( [] )
    const revokecheck = ref( [] )
    const { books } = storeToRefs( useBookdetailsStore() )


    const issue = computed( () =>
    {
        if ( issuecheck.value.length == 0 )

            return "Select the books to be issued"
        else
        {
            const text = issuecheck.value.map( e => books.value[ e ] ).toString()
            if ( text.length > 22 )
            {
                return `${ issuecheck.value.length } items selected`
            }
            return text
        }

    } )

    const revoke = computed( () =>
    {
        if ( revokecheck.value.length == 0 )

            return "Select the books to be revoked"
        else
        {
            const text = revokecheck.value.map( e => books.value[ e ] ).toString()
            if ( text.length > 22 )
            {
                return `${ revokecheck.value.length } items selected`
            }
            return text
        }

    } )

    async function submit ()
    {
        useLoadingStore().loading = true

        let bodyContent = new FormData()

        for ( const i of issuecheck.value )
        {
            bodyContent.append(
                "issue", i,
            )
        }

        for ( const i of revokecheck.value )
        {
            bodyContent.append(
                "revoke", i,
            )
        }

        let r = await fetchfunct( backurl + `admin/users/${ user.value.user_id }`, {
            method: "PUT", body: bodyContent,
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {
            editing.value = false

            r = await r.json()

            //changing the values in dom and resetting
            user.value.currently_issued_books = r.currently_issued_books
            user.value.no_of_issues = r.no_of_issues
            issuecheck.value.length = 0
            revokecheck.value.length = 0

            if ( r.response.errors.length == 0 )
            {
                useAlertStore().alertpush( [ { msg: 'The action is successful!', type: 'alert-success' } ] )
            }
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
    <h4 class="mb-3">User Current Issue Details <i @click="editing=!editing" title="Edit the user details"
            class="bi bi-pencil-square pointer-link" :style="(!editing)&&{'color':'gray'}"></i>
    </h4>
    <div class="row mb-3">
        <div class="col">Currently issued books</div>
        <div v-if="user.currently_issued_books.length==0" class="col text-muted">No books are currently
            used by
            the user.</div>
        <div v-else class="col">
            <table class="table table-bordered text-center">
                <thead>
                    <tr>
                        <th scope="col">Book name</th>
                        <th scope="col">Return date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="book in user.currently_issued_books">
                        <td>{{book.book_name}}</td>
                        <td>{{book.return_date}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="row mb-3" v-if="editing&&user.currently_issued_books.length!=Object.keys(books).length">
        <div class="col">Issue books to the user</div>
        <div class="col">
            <div class="dropdown-center">
                <button class="edit" type="button" data-bs-toggle="dropdown">
                    <span :class="['text', issuecheck.length==0&&'text-muted']">{{ issue }}</span><span
                        class="dropdown-toggle"></span>
                </button>
                <ul class="dropdown-menu">
                    <li v-for="(book_name,book_id) in books" :key="book_id">
                        <div v-if="!user.currently_issued_books.find(e=>e.book_id==book_id)">
                            &nbsp<input type="checkbox" :value="book_id" v-model="issuecheck"
                                class="form-check-input" />&nbsp
                            <label class="form-check-label">
                                {{ book_id }} : {{book_name}}
                            </label>&nbsp
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </div>


    <div class="row mb-3" v-if="editing&&!(user.currently_issued_books==0)">
        <div class="col">Revoke books to the user</div>
        <div class="col">
            <div class="dropdown-center">
                <button class="edit" type="button" data-bs-toggle="dropdown">
                    <span :class="['text', revokecheck.length==0&&'text-muted']">{{ revoke }}</span><span
                        class="dropdown-toggle"></span>
                </button>
                <ul class="dropdown-menu">
                    <li v-for="book in user.currently_issued_books" :key="book.book_id">
                        &nbsp<input type="checkbox" :value="book.book_id" v-model="revokecheck"
                            class="form-check-input" />&nbsp
                        <label class="form-check-label">
                            {{ book.book_id }} : {{book.book_name}}
                        </label>&nbsp
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <div class="row mb-3" v-if="editing">
        <div class="col-auto offset-md-6">
            <button type="submit" class='btn btn-outline-success' @click="submit">Submit</button>
        </div>
    </div>

</template>
<style scoped>
    .edit {
        height: 40px;
        width: 280px;
        background: rgb(131 127 127 / 10%);
        border: 1px solid var(--navbar-bg);
        border-radius: .375rem
    }

    .dropdown-toggle {
        float: right
    }

    .text {
        float: left
    }
</style>
