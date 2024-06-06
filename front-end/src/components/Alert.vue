<script setup>
defineProps({
  alerts: {
    type: Object,
    required: true
  }
})
function icon(type) {
  if (type == 'alert-success') {
    return '<i class="bi bi-check-circle-fill"></i>'
  }
  else if (type == 'alert-info') {
    return '<i class="bi bi-info-circle-fill"></i>'
  }
  else {
    return '<i class="bi bi-exclamation-triangle-fill"></i>'
  }
}
</script>

<template>
  <div v-for="alert in alerts">
    <div :class="['alert',alert.type,'alert-dismissible','mx-auto']" role="alert">
      <span v-html="icon(alert.type)"></span> {{ alert.msg }}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  </div>
</template>