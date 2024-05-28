<script setup>
defineProps({
  modal: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="modal fade" :id="modal.id" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="logoutModalLabel">{{ modal.title }}</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">{{ modal.body }}</div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <RouterLink :to="modal.link" tag="button" class="btn btn-dark">{{ modal.msg  }}</RouterLink>
          </div>
        </div>
    </div>
  </div>
</template>

