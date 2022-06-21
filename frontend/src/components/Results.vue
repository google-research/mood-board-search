<template>
  <div class="results">
    <div class="results-image-grid" ref="grid">
      <ResultImage class="result-image"
                   v-for="(image, index) in resultImages"
                   v-show="imageVisible(index)"
                   :viewMode="viewMode"
                   :key="index"
                   :image="image"
                   :project="project"
                   :neuralLens="neuralLens"
                   :shouldCalculateCrop="viewMode == 'crop' && imageVisible(index)"
                   :style="gridPosition(index)" />
      <template v-if="neuralLens === null || neuralLens.resultImages === null">
        <div class="placeholder-result-image"
             v-for="index in 100"
             :key="index"
             :style="gridPosition(index-1)" />
      </template>
      <div class="fade fill" v-if="neuralLens === null" />
    </div>
    <div class="load-more-container" v-if="viewMode == 'crop' && moreImagesToLoad">
      <button class="load-more-button studio-button"
              @click.prevent.stop="loadMoreButtonPressed">
        Load more
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import Vue, {PropType} from 'vue';
import ResultImage from '@/components/ResultImage.vue';

import {CAVServerImage} from '@/model/CAVImage';
import NeuralLens from '../model/NeuralLens';
import _ from 'lodash'
import Project from '../model/Project';
import imageInspectCache from '../model/imageInspectCache';

// [ grid-column, grid-row ]
const layout = [
  ["1 / span 4", "1 / span 4"],
  ["3 / span 4", "5 / span 4"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  /* 1 x 2 */
  ["span 3", "span 3"],
  ["span 3", "span 3"],
  /* 1 x 2 */
  ["span 3", "span 3"],
  ["span 3", "span 3"],
  /* 1 x 3 */
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  /* 1 x 3 */
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  /* 1 x 3 */
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  /* 1 x 3 */
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
]

export default Vue.extend({
  name: 'Results',
  props: {
    project: Object as PropType<Project>,
    neuralLens: Object as PropType<NeuralLens>,
    viewMode: String,
  },
  data() {
    return {
      cropImageCount: 10,
    }
  },
  mounted() {
  },
  computed: {
    resultImages(): CAVServerImage[] {
      return this.project?.neuralLens?.resultImages ?? [];
    },
    moreImagesToLoad(): boolean {
      return this.cropImageCount < this.resultImages.length
    },
  },
  methods: {
    gridPosition(index: number): Object {
      var col = 'span 1'
      var row = 'span 1'
      if (index < layout.length) {
        col = layout[index][0]
        row = layout[index][1]
      }
      return {
        'grid-column': col,
        'grid-row': row,
      }
    },
    imageVisible(index: number): boolean {
      if (this.viewMode == 'crop') {
        return index < this.cropImageCount;
      } else {
        return true;
      }
    },
    loadMoreButtonPressed(): void {
      this.cropImageCount += 12;

      this.$nextTick(() => {
        this.$emit('didChangeHeight')
      })
    }
  },
  watch: {
    'project.neuralLens': function (): void {
      // the lens changed. clear any pending crop tasks
      imageInspectCache.clearQueue()
      // reset number of crops to 10
      this.cropImageCount = 10;
      // precache the first 10
      if (this.project.neuralLens) {
        for (const image of this.resultImages.slice(0, 10)) {
          imageInspectCache.getTopCrops(image, this.project.neuralLens.cavID)
        }
      }
    }
  },
  components: {
    ResultImage,
  }
})
</script>

<style scoped lang="scss">
.results-image-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-auto-rows: minmax(10px, 1fr);
  gap: 10px;
  position: relative;
}
.results-image-grid::before {
  /* invisible element that sets the grid size */
  content: '';
  width: 0;
  padding-bottom: 100%;
  grid-row: 1 / 1;
  grid-column: 1 / 1;
}
.results-image-grid > *:first-child {
  /* put the first training image over that placeholder grid cell */
  grid-row-start: 1;
  grid-column-start: 1;
}
.result-image, .placeholder-result-image {
  background: #f9f9f9;
}
.fade {
  background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.00) 15%, #FFFFFF 30%);
}
.load-more-container {
  margin: 25px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
.load-more-button {
  padding-left: 20px;
  padding-right: 20px;
  background: #6980ff;

  &:active {
    background: #576de6;
  }
}
</style>
