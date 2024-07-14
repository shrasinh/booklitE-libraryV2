import { ref, reactive, nextTick } from 'vue'
import { defineStore } from 'pinia'

// used for search and random functionality
export const useSearchStore = defineStore( 'search', () =>
{
  const sections = ref( [] )
  const book_ids = ref( [] )
  return { sections, book_ids }
} )


// to guard the routes that requires authorization
export const useIdentityStore = defineStore( 'identity', () =>
{
  const identity = ref( [ 'Unauthenticated' ] )
  return { identity }
} )


// to display modal - the Modal component
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


// to push the alerts - the Alert component
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


// to show the spinner- the Spinner component
export const useLoadingStore = defineStore( 'loading', () =>
{
  const loading = ref( false )
  return { loading }
} )


// to change the theme - of various different elements
export const useThemeStore = defineStore( 'theme', () =>
{
  const theme = ref( 'light' )
  return { theme }
} )


// used by admin side - to get the section and language info required to create a book
export const useBookcreateStore = defineStore( 'bookcreate', () =>
{
  const sections = ref( [] )
  const languages = ref( {} )
  return { sections, languages }
} )


// used by admin side - to get the book info to assign/revoke books to users
export const useBookdetailsStore = defineStore( 'bookdetails', () =>
{
  const books = ref( [] )
  return { books }
} )
