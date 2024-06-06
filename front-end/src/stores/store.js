import { ref, reactive, nextTick } from 'vue'
import { defineStore } from 'pinia'

export const useSearchStore = defineStore('search', () => {
  const search = ref(0)
  return { search }
})

export const useIdentityStore = defineStore('identity', () => {
  const identity = ref(['Unauthenticated'])
  return { identity }
})

export const useModalStore = defineStore('modal', () => {

  const modal = reactive({})

  async function modalfunc(value) {
    // hide the previously shown modal
    modal.id ? bootstrap.Modal.getInstance(document.getElementById(modal.id)).hide() : ""

    modal.id = value.id
    modal.title = value.title
    modal.body = value.body
    modal.footer = value.footer
    await nextTick()
    new bootstrap.Modal(document.getElementById(modal.id)).show()
  }
  return { modal, modalfunc }
})

export const useAlertStore = defineStore('alert', () => {

  const alerts = ref([])

  function alertremove(time) {
    setTimeout(() => {
      alerts.value.length = 0
    }, time)
  }
  return { alerts, alertremove }
})

export const useLoadingStore = defineStore('loading', () => {
  const loading = ref(false)
})