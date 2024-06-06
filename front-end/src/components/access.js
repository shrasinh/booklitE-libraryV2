import { Form, Field, ErrorMessage } from 'vee-validate'
import { h } from 'vue'
import { object, string, ref } from "yup"
import { useIdentityStore, useModalStore, useAlertStore, useLoadingStore } from '../stores/store.js'
import { fetchfunct, checkerror } from './fetch.js'

const register_schema = object().shape({
    email: string().required().email(),
    username: string().required().min(4).max(32),
    password: string().required().min(8),
    confirm_password: string().oneOf([ref('password'), null], 'Password and confirmation password donot match'),
})

const register = {
    id: 'registerModal',
    title: 'Let\'s Get You Signed Up.',
    body: h(Form, { onSubmit: login_or_register, 'validation-schema': register_schema }, () => [
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "username", placeholder: 'Username' }), h(ErrorMessage, { class: "form-text", name: "username" })]),
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "email", placeholder: 'Email Address' }), h(ErrorMessage, { class: "form-text", name: "email" })]),
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "password", type: "password", placeholder: 'Password' }), h(ErrorMessage, { class: "form-text", name: "password" })]),
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "confirm_password", type: "password", placeholder: 'Reconfirm password' }), h(ErrorMessage, { class: "form-text", name: "confirm_password" })]),
        h('div', { class: 'd-grid gap-2' }, h('button', { class: 'btn btn-outline-primary' }, 'Register')),
    ]),
    footer: h('a', { href: "#login", onClick: () => useModalStore().modalfunc(login) }, "Already have an account? Login")
}

const login_schema = object().shape({
    username: string().required().min(4).max(32),
    password: string().required().min(8),
})

const login = {
    id: 'loginModal',
    title: 'Welcome Back!',
    body: h(Form, { onSubmit: login_or_register, 'validation-schema': login_schema }, () => [
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "username", placeholder: 'Username' }), h(ErrorMessage, { class: "form-text", name: "username" })]),
        h('div', { class: 'mb-3' }, [h(Field, { class: 'form-control', name: "password", type: "password", placeholder: 'Password' }), h(ErrorMessage, { class: "form-text", name: "password" })]),
        h('div', { class: 'd-grid gap-2' }, h('button', { class: 'btn btn-outline-primary' }, 'Login')),
    ]),
    footer: h('a', { href: "#register", onClick: () => useModalStore().modalfunc(register) }, "New user? Register"),
}

async function login_or_register(values, { resetForm }) {

    // hiding the bootstrap modal element
    bootstrap.Modal.getInstance(document.getElementById(useModalStore().modal.id)).hide()
    //resetting the form
    resetForm()
    //resetting the alerts
    useAlertStore().alertremove(0)

    useLoadingStore().loading = true
    //sending the login details
    let headersList = {
        "Content-Type": "application/json"
    }
    if (values.email) {
        var bodyContent = JSON.stringify({
            "username": values.username,
            "password": values.password,
            "email": values.email
        })
        var fetchurl = backurl + "register?include_auth_token"
    }
    else {
        var bodyContent = JSON.stringify({
            "username": values.username,
            "password": values.password,
        })
        var fetchurl = backurl + "login?include_auth_token"
    }

    let response = await fetchfunct(fetchurl, { method: "POST", body: bodyContent, headers: headersList })

    if (response.ok) {

        //getting the user role
        let data = await response.json()
        let r = await fetchfunct(backurl + "user/role", { headers: { "Authentication-Token": data.response.user.authentication_token } })
        if (r.ok) {
            useIdentityStore().identity = await r.json()
            sessionStorage.setItem("Authentication-Token", data.response.user.authentication_token)
            sessionStorage.setItem("Identity", JSON.stringify(useIdentityStore().identity))
            useAlertStore().alerts.push({ msg: 'You have successfully logged in!', type: 'alert-success' })
        }
        else {
            checkerror(r)
        }
    }
    else {
        checkerror(response)
    }
    useLoadingStore().loading = false
}

const logout = {
    id: 'logoutModal',
    title: 'Good Bye!',
    body: h('div', 'Do you want to logout?'),
    footer: h('button', { class: 'btn btn-secondary', onClick: () => logoutfunc() }, 'Confirm')
}

async function logoutfunc() {
    // hiding the bootstrap modal element
    bootstrap.Modal.getInstance(document.getElementById(useModalStore().modal.id)).hide()
    //resetting the alerts
    useAlertStore().alertremove(0)
    useLoadingStore().loading = true
    let r = await fetchfunct(backurl + "logout", { headers: { "Authentication-Token": sessionStorage.getItem("Authentication-Token") } })
    if (r.ok) {
        sessionStorage.removeItem('Authentication-Token')
        sessionStorage.removeItem('Identity')
        useIdentityStore().identity = ['Unauthenticated']
        useAlertStore().alerts.push({ msg: 'You have successfully logged out!', type: 'alert-success' })
    }
    else {
        checkerror(r)
    }
    useLoadingStore().loading = false
}

export { login, register, logout }