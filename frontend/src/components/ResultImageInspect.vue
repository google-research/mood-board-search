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
  <div class="inspect-result-image" @click.prevent.stop>
    <div class="overlay fill" v-if="!hasInspectData" @click.prevent.stop="overlayClicked">
      <InspectSpinner v-if="isLoading" class="spinner" />
      <img v-else class="eye-icon" src="./assets/eye_icon.svg">
    </div>
    <div v-if="hasInspectData && viewMode == 'inspect-heatmap'"
         class="heatmap fill"
         :style="{backgroundImage: `url(${inspectData.heatmap})`}">
    </div>
    <div class="crop fill" v-if="hasInspectData && viewMode == 'inspect-crop'">
      <div class="crop-rect" :style="{left: `${inspectData.top_crop.x*100}%`,
                                      top: `${inspectData.top_crop.y*100}%`,
                                      width: `${inspectData.top_crop.width*100}%`,
                                      height: `${inspectData.top_crop.height*100}%`,
                                      }">
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { CAVServerImage } from '../model/CAVImage';
import NeuralLens from '../model/NeuralLens';
import InspectSpinner from './InspectSpinner';
import cavServer from '../model/cavServer';

const inspectCache = {}

export default Vue.extend({
  name: 'ResultImageInspect',
  props: {
    image: CAVServerImage,
    neuralLens: NeuralLens,
    viewMode: String,
  },
  data() {
    return {
      isLoading: false,
      inspectCache,
    }
  },
  mounted() {
  },
  computed: {
    cacheKey() {
      return `${this.image.id}-${this.neuralLens.cavID}`
    },
    hasInspectData() {
      return this.inspectCache[this.cacheKey] !== undefined
    },
    inspectData() {
      return this.inspectCache[this.cacheKey];
    },
  },
  methods: {
    overlayClicked() {
      if (!this.isLoading) {
        this.loadInspectData().catch(console.error);
      }
    },
    async loadInspectData() {
      this.isLoading = true;
      try {
        const inspectData = await cavServer.inspectImage({
          image: this.image,
          cavID: this.neuralLens.cavID
        })
        Vue.set(inspectCache, this.cacheKey, inspectData)
      }
      finally {
        this.isLoading = false;
      }
    }
  },
  components: {
    InspectSpinner,
  }
})
</script>

<style scoped lang="scss">
.inspect-result-image {
}
.heatmap {
  background-color: #F9F9F9;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.overlay {
  background-color: rgba(255,255,255,0.8);
  cursor: pointer;

  &:hover {
    background-color: rgba(245,245,245,0.8);
  }
  &:active {
    background-color: rgba(235,235,235,0.8);
  }
  user-select: none;
}
.eye-icon {
  pointer-events: none;
  position: absolute;
  top: 50%;
  left: 50%;
  max-width: 50%;
  transform: translate(-50%, -50%);
}
.spinner {
  pointer-events: none;
  position: absolute;
  top: 50%;
  left: 50%;
  max-width: 80%;
  transform: translate(-50%, -50%);
}
.crop-rect {
  position: absolute;
  border: 3px solid #39fdd2;
}

</style>
