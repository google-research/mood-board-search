<template>
  <div class="result-image-crop" @click.prevent.stop>

    <div class="fill image" :style="cropStyle"></div>

    <transition name="fade">
      <div class="no-data-overlay fill" v-if="!cropSpec">
        <div class="loading-animation fill" v-if="isLoading">
          <svg viewBox="0 0 100 100" class="loading-animation-svg">
            <!-- the SVG renders at different sizes depending on the element's size, but the viewBox is always 100.
                 Scale the stroke-width so that it always renders at 2px.
                 The stroke is centered on the edge of the SVG, so we only see half of it - so specify double the
                 desired width here.
                  -->
            <rect x=0 y=0 width=100 height=100
                  :stroke-width="4*100/elementSize.width"
                  fill="none"
                  class="loading-snake"/>
          </svg>
        </div>
      </div>
    </transition>

    <div class="error-overlay" v-if="error"
         @click="loadCropData()">
      <img class="error-icon"
           src="./assets/error_icon.svg"
           v-tooltip="`Failed to get AI crop. <br>${error}<br><br>Click to retry.`">
    </div>

  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'
import { CAVServerImage } from '@/model/CAVImage'
import NeuralLens from '@/model/NeuralLens'
import cavServer, { CropSpec, CropsResponse } from '@/model/cavServer'
import mixins from 'vue-typed-mixins'
import AltKeyDownMixin from './mixins/AltKeyDownMixin';
import ObserveSizeMixin from './mixins/ObserveSizeMixin';
import imageInspectCache, { Ticket } from '@/model/imageInspectCache';

export default mixins(AltKeyDownMixin, ObserveSizeMixin).extend({
  name: 'ResultImageCrop',
  props: {
    image: Object as PropType<CAVServerImage>,
    neuralLens: Object as PropType<NeuralLens>,
    shouldCalculateCrop: Boolean,
  },
  data() {
    return {
      cropsTicket: null as Ticket<CropsResponse>|null,
    }
  },
  mounted() {
    this.loadCropDataIfNeeded()
  },
  computed: {
    cropSpec(): CropSpec|null {
      return this.cropsTicket?.result?.top_crop ?? null
    },
    isLoading(): boolean {
      return this.cropsTicket?.isLoading ?? false;
    },
    error(): Error|null {
      return this.cropsTicket?.error ?? null
    },
    cropStyle(): Partial<CSSStyleDeclaration> {
      const {cropSpec} = this;

      let cssX = 0.5, cssY = 0.5, cssWidth = 1.0, cssHeight = 1.0;

      if (cropSpec) {
        // css background position specifies an 'anchor' position for the image.
        // i.e. all the way left is 0%, all the way right is 100%.
        cssX = cropSpec.x / (1 - cropSpec.width);
        cssY = cropSpec.y / (1 - cropSpec.height);

        if (!isFinite(cssX)) {
          cssX = 0.5;
        }
        if (!isFinite(cssY)) {
          cssY = 0.5;
        }

        cssWidth = 1/cropSpec.width
        cssHeight = 1/cropSpec.height

        if (this.altKeyDown) {
          cssWidth = cssHeight = 1;
        }
      }

      return {
        backgroundImage: `url(` + this.image.url({format: 'jpeg'}) + `)`,
        backgroundPosition: `${cssX*100}% ${cssY*100}%`,
        backgroundSize: `${cssWidth*100}% ${cssHeight*100}%`,
      }
    }
  },
  methods: {
    loadCropDataIfNeeded() {
      if (this.shouldCalculateCrop) {
        this.cropsTicket = imageInspectCache.getTopCrops(this.image, this.neuralLens.cavID)
      }
    }
  },
  watch: {
    image() { this.loadCropDataIfNeeded() },
    neuralLens() { this.loadCropDataIfNeeded() },
    shouldCalculateCrop() { this.loadCropDataIfNeeded() },
  },
  components: {
  }

})
</script>

<style lang="scss" scoped>
.image {
  transition: background-size 0.10s ease;
}

.error-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background-color: rgba(0, 0, 0, 0.4);
}

.error-icon {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
}

.no-data-overlay {
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(2px);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease-out;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.loading-animation-svg {
  // not using '.fill' because on SVGs, height/width need to be set explicitly.
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 100%;
}

.loading-snake {
  stroke: #00ffc6;
  stroke-dasharray: 200 2000;
  stroke-linecap: square;
  animation-name: snake-run;
  animation-iteration-count: infinite;
  animation-duration: 1.5s;
  animation-timing-function: ease-in-out;
}
@keyframes snake-run {
  from {
    stroke-dashoffset: 200
  }
  to {
    stroke-dashoffset: -400
  }
}

</style>
