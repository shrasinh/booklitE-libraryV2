import { ref, reactive, nextTick } from 'vue'
import { defineStore } from 'pinia'

export const useSearchStore = defineStore( 'search', () =>
{
  const sections = ref( [] )
  const book_ids = ref( [] )
  return { sections, book_ids }
} )

export const useIdentityStore = defineStore( 'identity', () =>
{
  const identity = ref( [ 'Unauthenticated' ] )
  return { identity }
} )

export const useModalStore = defineStore( 'modal', () =>
{

  const modal = reactive( {} )

  async function modalfunc ( value )
  {

    // hide the previously shown modal
    modal.id && bootstrap.Modal.getInstance( document.getElementById( modal.id ) ).hide()

    modal.id = value.id
    modal.title = value.title
    modal.body = value.body
    modal.footer = value.footer

    // wait for the dom to change
    await nextTick()
    const newModalEl = document.getElementById( modal.id )

    // if the modal element does not have a event listener, then add one 
    // to emit 'modalclose' event for the form reset on modal closing
    if ( !newModalEl.hasAttribute( 'eventlistener' ) )
    {
      newModalEl.addEventListener( 'hidden.bs.modal', ( e ) =>
      {
        newModalEl.setAttribute( 'eventlistener', true )
        const modalform = document.querySelector( '.modal form' )
        modalform && modalform.dispatchEvent( new Event( 'modalclose' ) )
      } )
    }
    new bootstrap.Modal( newModalEl ).show()
  }
  return { modal, modalfunc }
} )

export const useAlertStore = defineStore( 'alert', () =>
{

  const alerts = ref( {} )

  function alertpush ( list )
  {
    //push elements with unique key to alerts object
    list.map( e => { alerts.value[ window.crypto.randomUUID() ] = e } )

    // scroll to the top position of the screen to view the new alerts
    window.scrollTo( 0, 0 )
  }
  return { alerts, alertpush }
} )

export const useLoadingStore = defineStore( 'loading', () =>
{
  const loading = ref( false )
  return { loading }
} )

export const useThemeStore = defineStore( 'theme', () =>
{
  const theme = ref( 'light' )
  return { theme }
} )

export const useBookcreateStore = defineStore( 'bookcreate', () =>
{
  const sections = ref( [] )
  const languages = ref( {} )
  return { sections, languages }
} )

export const useBookdetailsStore = defineStore( 'bookdetails', () =>
{
  const books = ref( {} )
  return { books }
} )