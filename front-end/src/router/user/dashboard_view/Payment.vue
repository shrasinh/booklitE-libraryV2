<script setup>
    import { ref, computed } from 'vue'
    import { useLoadingStore } from '../../../stores/store.js'
    import { fetchfunct, checkerror, checksuccess } from '../../../components/fetch.js'
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string, date } from "yup"

    const props = defineProps( [ 'user' ] )
    const user = ref( props.user )

    const payment = ref( { ...user.value.payment } ) // intermediate- can be changed by user, used for editing to prefill the input fields

    function next_month ()
    {
        let date = new Date()
        return new Date( date.setMonth( date.getMonth() + 1 ) )
    }

    const padZero = ( value ) => ( value < 10 ? `0${ value }` : `${ value }` );

    function formatted_date ( date )
    {
        let year = new Intl.DateTimeFormat( 'en', { year: 'numeric' } ).format( date );
        let month = padZero( new Intl.DateTimeFormat( 'en', { month: 'numeric' } ).format( date ) );
        return `${ year }-${ month }`
    }
    const next_month_date = formatted_date( next_month() )

    const compute_date = computed( {
        get () { return payment.value.expiry_date ? formatted_date( new Date( payment.value.expiry_date ) ) : next_month_date },
        set ( newdate )
        {
            payment.value.expiry_date = new Date( newdate ).toUTCString()
        }
    } )
    const editing = ref( false )

    const payment_schema = object().shape( {
        card_number: string().required().matches( /^[0-9]+$/, "Must be only digits" ).min( 12 ).max( 19 ),
        expiry_date: date().required().min( next_month_date, "Expiry Date must be greater than the present month" ),
        card_name: string().required().matches( /^[a-zA-Z]+$/, "Must be only english alphabets only!" ).strict(),
    } )


    async function submit ( values )
    {
        useLoadingStore().loading = true
        editing.value = false

        let bodyContent = new FormData()

        bodyContent.append(
            "cardno", values.card_number,
        )
        bodyContent.append(
            "expirydate", values.expiry_date,
        )
        bodyContent.append(
            "cardname", values.card_name,
        )

        let r = await fetchfunct( backurl + "user/paymentdetails", {
            method: "PUT", body: bodyContent
        } )
        if ( r.ok )
        {
            user.value.payment = { ...payment.value }
            !user.value.payment.expiry_date ? user.value.payment.expiry_date = new Date( compute_date.value ).toUTCString() : ''
            checksuccess( r )
        }
        else
        {
            checkerror( r )
            payment.value = { ...user.value.payment }
        }
        // stopping the loading screen
        useLoadingStore().loading = false
    } 
</script>

<template>
    <div class="text-center p-4">
        <h1 class="mb-3">Payment Details</h1>
        <div v-if="Object.keys(user.payment).length==0">No payment details found click on <em class="pointer-link"
                title="Enter the payment details" @click="editing=!editing" :style="(!editing)&&{'color':'gray'}">
                <i class="bi bi-plus-lg"></i>Enter payment details</em> to enter your payment details.</div>

        <span v-else class="pointer-link" :style="(!editing)&&{'color':'gray'}" title="Edit the payment details"
            @click="editing=!editing"><i class="bi bi-pencil-square pointer-link"></i> Edit your
            payment details.</span>
    </div>

    <div v-if="!editing&&Object.keys(user.payment).length>0">
        <div class="row mb-3 justify-content-center">
            <div class="col-lg-3 col text-end">Name on the card:</div>
            <div class="col-lg-3 col">
                {{ user.payment.card_name }}
            </div>
        </div>
        <div class="row mb-3 justify-content-center">
            <div class="col-lg-3 col text-end">Card number:</div>
            <div class="col-lg-3 col">
                {{ user.payment.card_number }}
            </div>
        </div>
        <div class="row mb-3 justify-content-center">
            <div class="col-lg-3 col text-end">Card expiry date:</div>
            <div class="col-lg-3 col">
                {{ user.payment.expiry_date }}
            </div>
        </div>
    </div>


    <Form v-if="editing" :validation-schema="payment_schema" @submit="submit">
        <div class="row mb-3 form-element justify-content-center">
            <div class="col-lg-3 col form-floating">
                <Field v-model="payment.card_name" class='form-control' name="card_name" placeholder='Name on the card'>
                </Field>
                <label>Name on the card</label>
                <ErrorMessage class="form-text" name="card_name"></ErrorMessage>
            </div>
        </div>

        <div class="row mb-3 form-element justify-content-center">
            <div class="col-lg-3 col form-floating">
                <Field v-model="payment.card_number" class='form-control' name="card_number" placeholder='Card number'
                    type="tel">
                </Field>
                <label>Card number</label>
                <ErrorMessage class="form-text" name="card_number"></ErrorMessage>
            </div>
        </div>

        <div class="row mb-3 form-element justify-content-center">
            <div class="col-lg-3 col form-floating">
                <Field v-model="compute_date" class='form-control' name="expiry_date" placeholder='expiry date of card'
                    type="month" :min="next_month_date"></Field>
                <label>Card expiry date</label>
                <ErrorMessage class="form-text" name="expiry_date"></ErrorMessage>
            </div>
        </div>

        <div class='row mb-3'>
            <div class="col text-center">
                <button type="submit" class='btn btn-outline-success'>Submit</button>
            </div>
        </div>
    </Form>

</template>