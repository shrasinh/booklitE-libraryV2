<script setup>

    const quotes = [ { quote: 'We read to know we are not alone.', speaker: 'C.S. Lewis ' },
    { quote: 'I lived in books more than I lived anywhere else.', speaker: 'Neil Gaiman ' },
    { quote: 'The best books... are those that tell you what you know already.', speaker: 'George Orwell ' } ]

</script>
<template>
    <div class="carousel slide carousel-fade text-end" data-bs-ride="carousel">
        <div class="carousel-inner">
            <div v-for="(quote,index) in quotes">
                <div :class="['carousel-item',(index==0)&&'active']" data-bs-interval="10000">
                    <figure>
                        <blockquote class="blockquote">
                            <p>{{ quote.quote }}</p>
                        </blockquote>
                        <figcaption class="blockquote-footer"><cite :title="quote.speaker">{{ quote.speaker }}</cite>
                        </figcaption>
                    </figure>
                </div>
            </div>
        </div>
    </div>
</template>