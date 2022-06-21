<template>
  <div style="position: relative; height: 0px; padding-top: 45.6%">
    <div class="row fill">
      <!-- HERO IMAGES -->
      <div class="grid hero-grid" style="width: 57.4%">
        <div class="hero-image"
            v-for="(image, index) in heroIndexes"
            :key="index"
            :style="gridPosition(index)"
            @click.alt="imageAltClicked(index)"
            @click.exact.prevent.stop="chooseImage(index)" >
          <div
            v-if="image"
            class="image fill"
            :style="{backgroundImage: `url('${image.url({format: 'jpeg'})}')`}" />
          <div
            v-else
            class="placeholder fill" >
            <div class="cross" />
          </div>
        </div>
      </div>
      <!-- LENS MOCKUP -->
      <div class="lens" style="width: calc(100% - 57.4%)">
        <div class="lens-border" />
        <div class="lens-crop">
          <div class="lens-container fill">
            <div class="grid lens-grid">
              <div class="hero-image"
                v-for="(image, index) in heroIndexes"
                :key="index"
                :style="gridPosition(index)">
                <div
                  v-if="image"
                  class="image fill"
                  :style="{backgroundImage: `url('${image.url({format: 'jpeg'})}')`}" />
                <div
                  v-else
                  class="lens-placeholder fill" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- <div class="chooser" /> -->
  </div>
</template>

<script>
import Vue from 'vue';
import Project from '../model/Project';
import ChooseImageDialog from './ChooseImageDialog';

const layout = [
  ["1 / span 3", "1 / span 3"],
  ["span 2", "span 2"],
  ["span 2", "span 2"],
  ["span 1", "span 1"],
  ["span 1", "span 1"],
  ["span 1", "span 1"],
]

export default Vue.extend({
  name: 'PublishHeroGrid',
  props: {
    project: Project,
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  computed: {
    heroIndexes() {
      return _.range(6).map(index =>
        this.project.publishInfo.heroImages[index]
      )
    }
  },
  methods: {
    gridPosition(index) {
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
    imageAltClicked(index) {
      const image = _.sample(this.project.positiveSet.images)
      this.$set(this.project.publishInfo.heroImages, index, image)
      this.project.setNeedsSave()
    },
    chooseImage(index) {
      this.$modal.show(ChooseImageDialog, {
        images: this.project.positiveSet.images,
        index: index,
        publishInfo: this.project.publishInfo
      }, {
        height: '80%'
      }, {
      'before-close': (event) => {
        this.project.setNeedsSave()
        }
      })
    },
  },
  components: {
  }
})
</script>

<style scoped>
.hero-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  position: relative;
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
.hero-image {
  position: relative;
  cursor: pointer;
}
.image {
  background-color: #aaa;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.placeholder {
  border: 2px dashed #E0E0E0;
  display: flex;
  justify-content: center;
  align-items: center;
}
.cross {
  width: 20px;
  height: 20px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/cross.svg);
}
.row {
  display: flex;
}
.lens {
  position: relative;
}
.lens-border {
  position: absolute;
  width: 100%;
  height: 0;
  padding-bottom: 100%;
  right: -13%;
  top: 50%;
  transform: translateY(-50%);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/lens_border.svg);
}
.lens-crop {
  position: absolute;
  width: 62.5%;
  height: 0;
  top: 50%;
  transform: translateY(-50%);
  right: 6%;

  overflow: hidden;
  border-radius: 500px;
  padding-bottom: 62.5%;
}
.lens-container {
  overflow: hidden;
  position: relative;
}
.lens-grid {
  width: 125%;
  transform: translateX(-16%);
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 3.5px;
  height: 100%;
}
.lens-grid > .hero-image {
  cursor: unset;
}
.lens-placeholder {
  background: #F7F7F7;
}
.chooser {
  position: fixed;
  top: 50px;
  bottom: 50px;
  width: 30%;
  background: blue;
}
</style>
