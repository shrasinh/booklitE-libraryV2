import { useAlertStore } from '../stores/store.js'

export async function fetchfunct(url, options) {
    options = Object.assign(Object.assign({ "Accept": "application/json" }, options.headers), options)
    useAlertStore().alertremove(60000)
    return fetch(url, options).catch(() => "Failed to fetch. Network error occured.")
}

export async function checkerror(response) {
    if (response.status) {
        let data = await response.json()
        for (const i of data.response.errors) {
            useAlertStore().alerts.push({ msg: i, type: 'alert-danger' })
        }
    }

    else {
        useAlertStore().alerts.push({ msg: response, type: 'alert-danger' })
    }
}