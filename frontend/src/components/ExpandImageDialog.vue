<template>
  <div class="expand-image-dialog">
    <div class="image-container">
      <img :src="image.url({format: 'jpeg'})" />
    </div>
  </div>
</template>

<script>
import cavServer from '@/model/cavServer';

export default {
  name: 'ExpandImageDialog',
  props: ['image'],
}
</script>

<style scoped>
.expand-image-dialog {
  padding: 20px;
  padding: 18px;
}
img {
  max-width: 100%;
}
</style>
