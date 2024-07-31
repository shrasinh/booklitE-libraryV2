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
        let r = await fetchfunct( backurl + "admin/users" )
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
            <h1 class="mb-md-3 p-2">All Users</h1>
        </div>
        <div class="col-auto p-4">
            <input class="form-control search-icon" placeholder="Search for a user..." v-model="search">
        </div>
    </div>

    <p v-if="users.length===0" class="text-muted mb-3 p-2">
        No users are present yet.</p>

    <div v-else>

        <div class="accordion" id="users">
            <div v-for="user in users" :key="user.user_id">
                <div class="accordion-item"
                    v-if="search.length==0|user.username.toLowerCase().includes(search.toLowerCase())">

                    <div class="accordion-header">
                        <div class="accordion-button collapsed row" data-bs-toggle="collapse"
                            :data-bs-target="'#collapse'+user.user_id">
                            <div class="col-md">
                                <div class="row">
                                    <div class="col-lg-4 col-auto">User Id</div>
                                    <div class="col-auto">{{user.user_id}}</div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-4 col-auto">User name</div>
                                    <div class="col-auto">{{user.username}}</div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-4 col-auto">Role</div>
                                    <div class="col-auto">{{user.roles}}</div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-4 col-auto">Issue limit</div>
                                    <div class="col-auto">{{user.issue_limit}}</div>
                                </div>
                            </div>
                            <div class="col-md">
                                <div class="row">
                                    <div class="col-lg-4 col-auto">Number of current issues</div>
                                    <div class="col-auto">{{user.currently_issued_books.length}}</div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-4 col-auto">Number of issues</div>
                                    <div class="col-auto">{{user.no_of_issues}}</div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-4 col-auto">Number of purchases</div>
                                    <div class="col-auto">{{user.no_of_purchase}}</div>
                                </div>
                            </div>
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
