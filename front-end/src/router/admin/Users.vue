<script setup>
    import { onMounted, ref } from 'vue'
    import { useLoadingStore, useBookdetailsStore } from '../../stores/store.js'
    import { fetchfunct, checkerror } from '../../components/fetch.js'
    import Useredit from './Useredit.vue'

    const users = ref( [] )
    const search = ref( "" )

    onMounted( async () =>
    {
        useLoadingStore().loading = true
        let r = await fetchfunct( backurl + "admin/users", {
            headers: {
                "Authentication-Token": localStorage.getItem(
                    "Authentication-Token" )
            }
        } )
        if ( r.ok )
        {
            r = await r.json()
            users.value = r.users
            useBookdetailsStore().books = r.books
        }
        else
        {
            checkerror( r )
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } )

</script>

<template>

    <div class='row mb-3 justify-content-between align-items-center'>
        <div class="col-auto">
            <h1 class="mb-3 p-2">All Users</h1>
        </div>
        <div class="col-auto">
            <input class="form-control search-icon" placeholder="Search for a user..." v-model="search">
        </div>
    </div>

    <p v-if="users.length===0" class="text-muted mb-3 p-2">
        No users are present yet.</p>

    <div v-else>

        <div class="row mx-auto text-center">

            <div class="col-1"><strong>User Id</strong></div>
            <div class="col-2"><strong>User Name</strong></div>
            <div class="col"><strong>Role</strong></div>
            <div class="col"><strong>Issue Limit</strong></div>
            <div class="col"><strong>Number of Currently Issued Books</strong></div>
            <div class="col"><strong>Total Number of Issues</strong></div>
            <div class="col"><strong>Total Number of Purchases</strong></div>

        </div>

        <div class="accordion" id="users">
            <div v-for="user in users">
                <div class="accordion-item"
                    v-if="search.length==0|user.username.toLowerCase().includes(search.toLowerCase())">

                    <div class="accordion-header row mx-auto">
                        <div class="accordion-button collapsed text-center" data-bs-toggle="collapse"
                            :data-bs-target="'#collapse'+user.user_id">
                            <div class="col-1">{{user.user_id}}</div>
                            <div class="col-2 break-word">{{user.username}}</div>
                            <div class="col">{{user.roles}}</div>
                            <div class="col">{{user.issue_limit}}</div>
                            <div class="col">{{user.currently_issued_books.length}}</div>
                            <div class="col">{{user.no_of_issues}}</div>
                            <div class="col">{{user.no_of_purchase}}</div>
                        </div>
                    </div>

                    <div :id="'collapse'+user.user_id" class="accordion-collapse collapse" data-bs-parent="#users">
                        <div class="accordion-body">
                            <Useredit :user="user"></Useredit>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>


</template>
