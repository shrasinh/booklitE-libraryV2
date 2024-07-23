<script setup>
    const filter = defineModel()
</script>
<template>
    <div class="dropdown" title="filter search results">
        <button class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown">
            <i class="bi bi-funnel-fill"></i>
        </button>
        <ul class="dropdown-menu">
            <li class="dropdown-item disabled">
                <div class="text-muted">Filter by</div>
            </li>
            <li class="dropdown-item">
                <div class="form-check">
                    <input type="radio" class="form-check-input" value="section" v-model="filter" />
                    <label class="form-check-label">Section</label>
                </div>
            </li>
            <li class="dropdown-item">
                <div class="form-check">
                    <input type="radio" class="form-check-input" value="book" v-model="filter" />
                    <label class="form-check-label">Book</label>
                </div>
            </li>
            <li class="dropdown-item">
                <div class="form-check">
                    <input type="radio" class="form-check-input" value="author" v-model="filter" />
                    <label class="form-check-label">Author</label>
                </div>
            </li>
        </ul>
    </div>
</template>