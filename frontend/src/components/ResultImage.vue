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
  <div class="result-image"
       @click.prevent.stop="expandImage"
       @contextmenu.prevent.stop="openContextMenu"
       :class="{ selected }">

    <div class="bg fill" key="bg"
         :style="{backgroundImage: `url(${image.url({format: 'thumbnail'})})`}" />

    <VueContext ref="menu" :lazy="true" @open="selected=true" @close="selected=false">
      <li>
        <a href="#"
           @click.prevent.stop="$refs.menu.close(); expandImage($event)">Expand image</a>
      </li>
      <li v-if="!isDisliked">
        <a href="#"
           @click.prevent.stop="$refs.menu.close(); dislike($event)">Add to ‘It is not…’</a>
      </li>
      <li v-else>
        <a href="#"
           @click.prevent.stop="$refs.menu.close(); unDislike($event)">Remove from ‘It is not…’</a>
      </li>
    </VueContext>

    <div v-if="isDisliked"
         class="icon-dislike">
      <div class="tooltip-container fill"
           v-if="isDislikedButStillAppearsInResults"
           @click.prevent.stop
           v-tooltip.bottom-start="{
             content: `
              <h5>Why is this image here?</h5>
              <p>It’s still a match for your CAV - try<br>refining your training images further.</p>
             `,
             html: true,
             offset: 3,
           }" />
    </div>

    <div class="menu-button"
         v-if="viewMode.startsWith('inspect')"
         @click.prevent.stop="openContextMenu" />

    <ResultImageCrop v-show="viewMode == 'crop'"
                     class="fill crop"
                     :image="image"
                     :neuralLens="neuralLens"
                     :shouldCalculateCrop="shouldCalculateCrop" />

    <ResultImageInspect v-show="viewMode.startsWith('inspect') && !altKeyDown"
                        class="fill inspect"
                        :image="image"
                        :neuralLens="neuralLens"
                        :viewMode="viewMode" />
  </div>
</template>

<script lang="ts">
import Vue, {PropType} from 'vue';
import { CAVServerImage, ServerTrainingImage } from '../model/CAVImage';
import ResultImageInspect from './ResultImageInspect.vue';
import ResultImageCrop from './ResultImageCrop.vue';
import ExpandImageDialog from './ExpandImageDialog.vue';
import NeuralLens from '../model/NeuralLens';
import VueContext from 'vue-context';
import Project from '../model/Project';
import notificationCenter from "@/model/notificationCenter";
import mixins from 'vue-typed-mixins'
import AltKeyDownMixin from './mixins/AltKeyDownMixin';

export default mixins(AltKeyDownMixin).extend({
  name: 'ResultImage',
  props: {
    image: Object as PropType<CAVServerImage>,
    neuralLens: Object as PropType<NeuralLens>,
    viewMode: String,
    project: Object as PropType<Project>,
    shouldCalculateCrop: Boolean,
  },
  data() {
    return {
      selected: false,
    }
  },
  mounted() {
    notificationCenter.$on('context-menu-will-open', this.contextMenuWillOpen)
  },
  beforeDestroy() {
    notificationCenter.$off('context-menu-will-open', this.contextMenuWillOpen)
  },
  computed: {
    isDisliked(): boolean {
      const negativeSetIds = this.project.negativeSet.images.map(i => {
        if (i instanceof CAVServerImage) {
          return i.id
        } else {
          return 'uploading'
        }
      })

      return negativeSetIds.includes(this.image.id)
    },
    isDislikedButStillAppearsInResults(): boolean {
      if (!this.isDisliked) return false;

      return (this.neuralLens.snapshotId == this.project.snapshotId)
    },
  },
  methods: {
    openContextMenu(event: any) {
      notificationCenter.$emit('context-menu-will-open', this.$refs.menu)
      const menu = this.$refs.menu as any;
      menu.open(event)
    },
    contextMenuWillOpen() {
      const menu = this.$refs.menu as any;
      menu.close()
    },
    dislike() {
      const trainingImage = new ServerTrainingImage(this.image.id, {
        userGenerated: this.image.userGenerated
      })
      trainingImage.weight = 4;

      this.project.negativeSet.addImages([trainingImage], {atFront: true})
    },
    unDislike() {
      const trainingImagesToRemove = this.project.negativeSet.images.filter(i => (
        i instanceof CAVServerImage && i.id === this.image.id
      ))
      trainingImagesToRemove.forEach(i => this.project.negativeSet.removeImage(i))
    },
    expandImage() {
      this.$modal.show(ExpandImageDialog, {
        image: this.image,
        neuralLens: this.neuralLens,
        viewMode: this.viewMode,
      }, {
        height: '600px'
      })
    },
  },
  components: {
    ResultImageInspect,
    ResultImageCrop,
    VueContext,
  }
})
</script>

<style scoped lang="scss">
.result-image {
  position: relative;

  &.selected::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    border: 3px solid #3b59ff;
  }
}
.bg {
  background-color: #F9F9F9;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.overlay {
  background-color: rgba(255,255,255,0.8);
}
.icon-dislike {
  top: 3px;
  left: 3px;
  width: 21px;
  height: 21px;
  position: absolute;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/icon_dislike.svg);

  .tooltip-container {
    cursor: help;
  }
}
.menu-button {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 21px;
  height: 21px;
  opacity: 0;
  cursor: pointer;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/icon_menu.svg);
  transition: all ease 0.15s;

  .result-image:hover & {
    opacity: 1;
  }
}
</style>
