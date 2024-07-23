<script setup>
    import { ref, computed } from 'vue'
    import { useLoadingStore, useAlertStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'
    import Starrating from '../../../components/Starrating.vue'

    const props = defineProps( [ 'rating' ] )
    const original = ref( props.rating )

    const rate = ref( original.value.rating )
    const feedback = ref( original.value.feedback )
    const editing = ref( false )

    const title = computed( () =>
    {
        if ( rate.value == '5' )
        {
            return "Very good! 😊"
        }
        else if ( rate.value == '4' )
        {
            return "Good! 😌"
        }
        else if ( rate.value == '3' )
        {
            return "Average 😑"
        }
        else if ( rate.value == '2' )
        {
            return "Poor 😓"
        }
        else if ( rate.value == '1' )
        {
            return "Very poor! 😔"
        }

    } )
    async function submit ()
    {
        useLoadingStore().loading = true

        let bodyContent = new FormData()

        bodyContent.append(
            "rating", rate.value,
        )
        bodyContent.append(
            "feedback", feedback.value ? feedback.value : "",

        )
        if ( original.value.rating_id )
        {
            let r = await fetchfunct( backurl + `/user/ratings/edit/${ original.value.rating_id }`, {
                method: "PUT", body: bodyContent
            } )
            if ( r.ok )
            {
                editing.value = false
                original.value.rating = rate.value
                original.value.feedback = feedback.value// changing the parent data
                checksuccess( r )
            }
            else
            {
                checkerror( r )
                rate.value = original.value.rating
                feedback.value = original.value.feedback// resetting the child data to the original data
            }
        }
        else
        {
            let r = await fetchfunct( backurl + `/user/ratings/create/${ original.value.book_id }`, {
                method: "POST", body: bodyContent
            } )
            if ( r.ok )
            {
                r = await r.json()
                // changing the parent data
                original.value.rating_id = r.rating_id
                original.value.rating_date = new Date().toUTCString()
                original.value.rating = rate.value
                original.value.feedback = feedback.value
                useAlertStore().alertpush( [ { msg: 'The rating is successfully given!', type: 'alert-success' } ] )
            }
            else
            {
                checkerror( r )
            }
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } 
</script>
<template>
    <h4 v-if="original.rating_id" class="mb-3">Rating Details <i @click="editing=!editing" title="Edit the rating"
            class="bi bi-pencil-square pointer-link" :style="(!editing)&&{'color':'gray'}"></i>
    </h4>
    <h4 v-else class="mb-3">
        Give Rating
    </h4>
    <div v-if="original.rating_id&&!editing">
        <div class="row mb-3">
            <div class="col-md">Rating</div>
            <div class="col-md">
                <Starrating :rating="original.rating"></Starrating>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-md">Feedback</div>
            <div v-if="original.feedback" class="col-md">{{ original.feedback}}</div>
            <div v-else class="col-md text-muted">No feedback given</div>
        </div>
    </div>
    <div v-if="!original.rating_id||editing">

        <div class="row mb-lg-3 mb-4">
            <div class="col-md">How much rating would you like to give the book? (1-very poor, 5-very good)</div>
            <div class="col-md">
                <div class="row align-items-center">
                    <div class="col-auto">
                        <div class="rate">
                            <input type="radio" :id="'star5'+original.book_id" name="rate" value="5" v-model="rate" />
                            <label :for="'star5'+original.book_id" title="Very good">5 stars</label>
                            <input type="radio" :id="'star4'+original.book_id" name="rate" value="4" v-model="rate" />
                            <label :for="'star4'+original.book_id" title="Good">4 stars</label>
                            <input type="radio" :id="'star3'+original.book_id" name="rate" value="3" v-model="rate" />
                            <label :for="'star3'+original.book_id" title="Average">3 stars</label>
                            <input type="radio" :id="'star2'+original.book_id" name="rate" value="2" v-model="rate" />
                            <label :for="'star2'+original.book_id" title="Poor">2 stars</label>
                            <input type="radio" :id="'star1'+original.book_id" name="rate" value="1" v-model="rate" />
                            <label :for="'star1'+original.book_id" title="Very poor">1 star</label>
                        </div>
                    </div>
                    <div class="col-auto">
                        {{ title }}
                    </div>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-md">Tell us why you like or dislike the book? (Optional)</div>
            <div class="col-md">
                <textarea v-model="feedback" class="form-control" cols="100" rows="10"
                    placeholder="feedback"></textarea>
            </div>
        </div>
        <div class='row mb-3'>
            <div class="col offset-md-6">
                <button @click="submit" class="btn btn-outline-success" :disabled="!rate">Submit</button>
            </div>
        </div>
    </div>
</template>
<style scoped>

    .rate {
        float: left;
        height: 46px;
    }

    .rate:not(:checked)>input {
        position: absolute;
        top: -9999px;
    }

    .rate:not(:checked)>label {
        float: right;
        width: 1em;
        overflow: hidden;
        white-space: nowrap;
        cursor: pointer;
        font-size: 30px;
        color: #ccc;
    }

    .rate:not(:checked)>label:before {
        content: '★ ';
    }

    .rate>input:checked~label {
        color: #ffc700;
    }

    .rate:not(:checked)>label:hover,
    .rate:not(:checked)>label:hover~label {
        color: #deb217;
    }

    .rate>input:checked+label:hover,
    .rate>input:checked+label:hover~label,
    .rate>input:checked~label:hover,
    .rate>input:checked~label:hover~label,
    .rate>label:hover~input:checked~label {
        color: #c59b08;
    }
</style>