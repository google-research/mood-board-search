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
  <div class="training-image-grid"
      :class="{dragging: numPlaceholderImages > 0, empty: empty && imageSet.isPositive}"
      @dragenter="dragHandler.dragenter($event)"
      @dragover="dragHandler.dragover($event)"
      @dragleave="dragHandler.dragleave($event)"
      @drop="dragHandler.drop($event)">
    <div class="placeholder fill"
        v-if="empty && imageSet.isPositive">
      <div class="spacer" style="height: 92px"/>
      <div class="message">
        Drag and drop<br>images that best <span style="color: #3B59FF">represent</span> your chosen concept
      </div>
      <div class="tips">
        <span style="font-weight: 500">Tips</span><br>
        Aim for 50+ images<br>
        Use square ratio images<br>
        Try cropping to focus what the CAV sees
      </div>
    </div>
    <TrainingImage v-for="image in imageSet.images"
                  :key="image.vueKey"
                  :image="image"
                  :positive="imageSet.isPositive"
                  @delete="imageSet.removeImage($event)"
                  @upweight="imageSet.upweightImage($event)"
                  @downweight="imageSet.downweightImage($event)"
                  class="training-image"
                  :class="{big: image.weight > 1}" />
    <div v-for="n in numPlaceholderImages" :key="`placeholder-${n}`" class="drop-placeholder"></div>
    <div v-for="n in numEmptyImages" :key="`empty-${n}`" class="empty-placeholder"></div>
    <div class="fade fill" v-if="numEmptyImages > 0" />
  </div>
</template>

<script>
import TrainingImageSet from '../model/TrainingImageSet';
import ImageDragHandler from './ImageDragHandler';
import TrainingImage from './TrainingImage.vue';
import Vue from 'vue';

export default Vue.extend({
  name: 'TrainingImageGrid',
  props: {
    imageSet: TrainingImageSet,
  },
  data() {
    return {
      dragHandler: null,
    }
  },
  mounted() {
    this.dragHandler = new ImageDragHandler(this.$el, imageFiles => {
      this.imageSet.addImageFiles(imageFiles)
    });
  },
  computed: {
    numPlaceholderImages() {
      if (!this.dragHandler) {
        return 0
      }
      return this.dragHandler.imagesAboutToDrop
    },
    numEmptyImages() {
      if (this.empty && !this.imageSet.isPositive && this.numPlaceholderImages == 0) {
        return 20;
      }

      return 0;
    },
    empty() {
      return this.imageSet.images.length === 0
    }
  },
  components: {
    TrainingImage,
  }
})
</script>

<style scoped>
.training-image-grid {
  /* min-height: 300px; */
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-flow: row dense;
  grid-auto-rows: 1fr;
  gap: 10px;
  position: relative;
}

.training-image-grid.dragging::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background: rgba(59,89,255,0.05);
  border: 3px solid #3B59FF;
  border-radius: 8px;
}

.training-image-grid::before {
  /* invisible element that sets the grid size */
  content: '';
  width: 0;
  padding-bottom: 100%;
  grid-row: 1 / 1;
  grid-column: 1 / 1;
}

.training-image-grid > *:first-child {
  /* put the first training image over that placeholder grid cell */
  grid-row-start: 1;
  grid-column-start: 1;
}

.training-image.big {
  grid-row-end: span 2;
  grid-column-end: span 2;
}

.drop-placeholder {
  background: #f9f9f9;
}
.empty-placeholder {
  background: #f9f9f9;
}
.empty {
  min-height: 410px;
}
.placeholder {
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 30px;

}
.message {
  max-width: 290px;
  font-weight: 700;
  font-size: 20px;
  color: #454545;
  letter-spacing: 0.29px;
  text-shadow: 0 0 10px #FFFFFF;
}
.tips {
  font-family: Roboto, sans-serif;
  font-size: 12px;
  color: #454545;
  letter-spacing: 0.17px;
  text-align: center;
}
.fade {
  background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, #FFFFFF 50%);
}
</style>
