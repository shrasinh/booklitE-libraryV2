import { Form, Field, ErrorMessage } from 'vee-validate'
import { h } from 'vue'
import { object, string, ref } from "yup"
import { useIdentityStore, useModalStore, useAlertStore, useLoadingStore } from '../stores/store.js'
import { fetchfunct, checkerror } from './fetch.js'
import router from '../router/index.js'


const register_schema = object().shape( {
    email: string().trim().required().email().strict(),
    username: string().trim().matches( /^[\p{L}\p{N}]+$/u, "Must be unicode letters and numbers only." ).required().min( 4 ).max( 32 ).strict(),
    password: string().matches( /^(?!(^\s+$))/, 'Blank-spaces only password is not allowed.' ).required().min( 8 ).strict(),
    confirm_password: string().oneOf( [ ref( 'password' ), null ], 'Password and confirmation password donot match' ).strict(),
} )

const register = {
    id: 'registerModal',
    title: 'Let\'s Get You Signed Up.',
    body: h( Form, { onSubmit: login_or_register, onModalclose: ( e ) => e.target.reset(), 'validation-schema': register_schema }, () => [
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "username", autocomplete: 'username', placeholder: 'username' } ), h( 'label', 'Username' ), h( ErrorMessage, { class: "form-text", name: "username" } ) ] ),
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "email", placeholder: 'email' } ), h( 'label', 'Email Address' ), h( ErrorMessage, { class: "form-text", name: "email" } ) ] ),
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "password", type: "password", autocomplete: 'new-password', placeholder: 'password' } ), h( 'label', 'Password' ), h( ErrorMessage, { class: "form-text", name: "password" } ) ] ),
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "confirm_password", type: "password", autocomplete: 'new-password', placeholder: 'confirm password' } ), h( 'label', 'Reconfirm password' ), h( ErrorMessage, { class: "form-text", name: "confirm_password" } ) ] ),
        h( 'div', { class: 'd-grid gap-2' }, h( 'button', { class: 'btn btn-outline-primary' }, 'Register' ) ),
    ] ),
    footer: h( 'a', { class: 'pointer-link', onClick: () => useModalStore().modalfunc( login ) }, "Already have an account? Login" )
}

const login_schema = object().shape( {
    username: string().trim().matches( /^[\p{L}\p{N}]+$/u, "Must be unicode letters and numbers only." ).required().min( 4 ).max( 32 ).strict(),
    password: string().matches( /^(?!(^\s+$))/, 'Blank-spaces only password is not allowed.' ).required().min( 8 ).strict(),
} )

const login = {
    id: 'loginModal',
    title: 'Welcome Back!',
    body: h( Form, { onSubmit: login_or_register, onModalclose: ( e ) => e.target.reset(), 'validation-schema': login_schema }, () => [
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "username", autocomplete: 'username', placeholder: 'username' } ), h( 'label', 'Username' ), h( ErrorMessage, { class: "form-text", name: "username" } ) ] ),
        h( 'div', { class: 'form-floating mb-3 form-element' }, [ h( Field, { class: 'form-control', name: "password", type: "password", autocomplete: 'current-password', placeholder: 'password' } ), h( 'label', 'Password' ), h( ErrorMessage, { class: "form-text", name: "password" } ) ] ),
        h( 'div', { class: 'd-grid gap-2' }, h( 'button', { class: 'btn btn-outline-primary' }, 'Login' ) ),
    ] ),
    footer: h( 'a', { class: 'pointer-link', onClick: () => useModalStore().modalfunc( register ) }, "New user? Register" ),
}

async function login_or_register ( values, { resetForm } )
{

    // hiding the bootstrap modal element
    bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()
    //resetting the form
    resetForm()
    // start the spinner/loading screen
    useLoadingStore().loading = true
    //sending the login details
    let headersList = {
        "Content-Type": "application/json"
    }
    if ( values.email )
    {
        var bodyContent = JSON.stringify( {
            "username": values.username,
            "password": values.password,
            "email": values.email
        } )
        var fetchurl = backurl + "register?include_auth_token"
    }
    else
    {
        var bodyContent = JSON.stringify( {
            "username": values.username,
            "password": values.password,
        } )
        var fetchurl = backurl + "login?include_auth_token"
    }

    let response = await fetchfunct( fetchurl, { method: "POST", body: bodyContent, headers: headersList } )

    if ( response.ok )
    {
        //getting the user role
        let data = await response.json()
        let r = await fetchfunct( backurl + "user/role", { headers: { "Authentication-Token": data.response.user.authentication_token } } )
        if ( r.ok )
        {
            useIdentityStore().identity = await r.json()
            localStorage.setItem( "Authentication-Token", data.response.user.authentication_token )
            localStorage.setItem( "Identity", JSON.stringify( useIdentityStore().identity ) )
            useAlertStore().alertpush( [ { msg: 'You have successfully logged in!', type: 'alert-success' } ] )
        }
        else
        {
            checkerror( r )
        }
    }
    else
    {
        checkerror( response )
    }
    // stopping the loading screen
    useLoadingStore().loading = false
}

const logout = {
    id: 'logoutModal',
    title: 'Good Bye!',
    body: h( 'div', 'Do you want to logout?' ),
    footer: h( 'button', { class: 'btn btn-outline-primary', onClick: () => logoutfunc() }, 'Confirm' )
}

async function logoutfunc ()
{
    // hiding the bootstrap modal element
    bootstrap.Modal.getInstance( document.getElementById( useModalStore().modal.id ) ).hide()
    // starting the loading screen
    useLoadingStore().loading = true
    let r = await fetchfunct( backurl + "logout", { headers: { "Authentication-Token": localStorage.getItem( "Authentication-Token" ) } } )
    if ( r.ok || r.status == 401 )
    {   // logout is successfully or the authentication token has expired
        localStorage.removeItem( 'Authentication-Token' )
        localStorage.removeItem( 'Identity' )
        useIdentityStore().identity = [ 'Unauthenticated' ]
        router.push( '/' )
        useAlertStore().alertpush( [ { msg: 'You have successfully logged out!', type: 'alert-success' } ] )
    }
    else
    {
        checkerror( r )
    }
    // stopping the loading screen
    useLoadingStore().loading = false
}

export { login, register, logout }