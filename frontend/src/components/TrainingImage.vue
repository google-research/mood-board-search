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
  <div class="training-image"
       :class="{selected}"
       @contextmenu.prevent="openContextMenu">
    <div class="bg"
         :style="{backgroundImage: `url('${image.url({format: 'thumbnail'})}')`}">
    </div>
    <div class="loading-overlay" v-if="image.isUploading">
      <div class="spinner"></div>
    </div>
    <div class="error-overlay" v-if="!image.isUploading && image.errorDescription"
         @click="image.tryUpload()">
      <img class="error-icon" src="./assets/error_icon.svg">
    </div>
    <div class="menu-button" @click="openContextMenu"></div>

    <VueContext ref="menu" :lazy="true" @open="selected=true" @close="selected=false">
      <li v-if="image.errorDescription">
        <a :class="{disabled: true}"
           style="color: #f7afca"
           @click.prevent.stop>Upload failed: {{image.errorDescription}}</a>
      </li>
      <li v-if="image.errorDescription">
        <a href="#"
           @click.prevent="image.tryUpload()">Retry upload</a>
      </li>
      <hr v-if="image.errorDescription">
      <li>
        <!-- TODO: remove v-if="positive" when negative set supports up/downweight -->
        <a href="#"
           v-if="positive"
           :class="{disabled: image.weight > 1}"
           @click.prevent="onContextMenuUpweight">Upweight image</a>
      </li>
      <li>
        <!-- TODO: remove v-if="positive" when negative set supports up/downweight -->
        <a href="#"
           v-if="positive"
           :class="{disabled: image.weight == 1}"
           @click.prevent="onContextMenuDownweight">Downweight image</a>
      </li>
      <li>
        <a href="#"
           class="destructive"
           @click.prevent="onContextMenuDelete">Delete image</a>
      </li>
    </VueContext>
  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue';
import { CAVTrainingImage } from '../model/CAVImage'
import { VueContext } from 'vue-context';
import notificationCenter from "@/model/notificationCenter";

export default Vue.extend({
  name: 'TrainingImage',
  props: {
    image: Object as PropType<CAVTrainingImage>,
    positive: Boolean,
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
  methods: {
    onContextMenuUpweight(event: Event) {
      if (this.image.weight > 1) {
        event.stopPropagation()
        return;
      }
      this.$emit('upweight', this.image);
    },
    onContextMenuDownweight(event: Event) {
      if (this.image.weight == 1) {
        event.stopPropagation()
        return;
      }
      this.$emit('downweight', this.image);
    },
    onContextMenuDelete() {
      this.$emit('delete', this.image);
    },
    openContextMenu(event: Event) {
      notificationCenter.$emit('context-menu-will-open', this.$refs.menu)
      const menu = this.$refs.menu as any
      menu.open(event)
    },
    contextMenuWillOpen(event: any) {
      const menu = this.$refs.menu as any
      menu.close()
    },
  },
  components: {
    VueContext,
  }
})
</script>

<style lang="scss" scoped>

.training-image {
  position: relative;

  // for debugging -  way too small in reality
  min-height: 20px;
  min-width: 20px;

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
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background-color: #aaa;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.loading-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background-color: rgba(0, 0, 0, 0.4);
}

.spinner {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

@keyframes spinner {
  to {transform: rotate(360deg);}
}

.spinner:before {
  content: '';
  box-sizing: border-box;
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin-top: -10px;
  margin-left: -10px;
  border-radius: 50%;
  border: 2px solid #ccc;
  border-top-color: transparent;
  animation: spinner .8s linear infinite;
}

.error-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background-color: rgba(200, 0, 0, 0.4);
}

.error-icon {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
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
}

.training-image:hover .menu-button {
  opacity: 1;
}

</style>

<style lang="scss">
/* context menu styling */

@import '~vue-context/src/sass/vue-context';

.v-context {
  &, & ul {
    font-family: Roboto, sans-serif;
    color: #5E5E5E;
    font-size: 13px;
    letter-spacing: 0.52px;
    // line-height: 33px;

    padding: 5px 0;
    border: none;
    border-radius: 0;
    background: #FFFFFF;
    box-shadow: 0 2px 15px -5px rgba(0,0,0,0.50);

    > li {
      > a {
        padding: 5px 12px;

        &:hover,
        &:focus {
          background: #3b59ff;
          color: white;
          &.destructive {
            background: #ff005e
          }
        }

        &.disabled {
          color: #dbdbdb;
          background: transparent;
          cursor: default;
        }
      }
    }
    > hr {
        margin: 4px 0px;
        border: none;
        border-top: 1px solid #eaeaea;
    }
  }
}
</style>
