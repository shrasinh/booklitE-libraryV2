<script setup>
    import Stats from './Stats.vue';
</script>

<template>

    <ul class="nav nav-tabs justify-content-end">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#stats">Library
                stats</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#export">Export library
                details</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#monthly">Monthly
                details</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade active show" id="stats" tabindex="0">
            <Stats></Stats>
        </div>
        <div class="tab-pane fade" id="export" tabindex="0">
            <Stats></Stats>
        </div>
        <div class="tab-pane fade" id="monthly" tabindex="0">
            <Stats></Stats>
        </div>
    </div>

</template>
<style scoped>
    .nav-link {
        color: var(_--navbar-bg)
    }
</style>