<script setup>

  import { useModalStore } from '../stores/store.js'
  import { storeToRefs } from 'pinia'

  const { modal } = storeToRefs( useModalStore() )

</script>

<template>
  <div class="modal fade" :id="modal.id" tabindex="-1">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <b>{{modal.title}}</b>
          </h1>
          <button class="btn btn-outline-danger" data-bs-dismiss="modal"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-body">
          <component :is="()=>modal.body"></component>
        </div>
        <div class="modal-footer">
          <component :is="()=>modal.footer"></component>
        </div>
      </div>
    </div>
  </div>
</template>
