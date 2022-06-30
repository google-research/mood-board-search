<!--
 Copyright 2022 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<template>
  <div class="choose-image-dialog">
    <h2>Choose a hero image</h2>
    <div class="grid">
      <div class="image"
        v-for="(image, index) in images"
        :key="index"
        @click.exact="done(image)"
        :style="{backgroundImage: `url('${image.url({format: 'thumbnail'})}')`}" />
    </div>
  </div>
</template>

<script>

export default {
  name: 'ChooseImageDialog',
  props: ['images', 'index', 'publishInfo'],
  methods: {
    done(image) {
      this.$set(this.publishInfo.heroImages, this.index, image)
      this.$emit('close')

    },
  },
}
</script>

<style scoped>
.choose-image-dialog {
  padding: 18px;
  padding-top: 0px;
  height: 100%;
  overflow-y: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 1fr;
  gap: 10px;
  position: relative;
  margin-top: -10px;
}
.grid::before {
  /* invisible element that sets the grid size */
  content: '';
  width: 0;
  padding-bottom: 100%;
  grid-row: 1 / 1;
  grid-column: 1 / 1;
}
.grid > *:first-child {
  /* put the first training image over that placeholder grid cell */
  grid-row-start: 1;
  grid-column-start: 1;
}
.image {
  cursor: pointer;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
h2 {
  font-weight: 500;
  font-size: 18px;
  color: #3B59FF;
  letter-spacing: 0.26px;
  text-align: center;
  position: sticky;
  top: 0px;
  z-index: 10;
  background: white;
  line-height: 60px;
}
</style>
