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
  <div class="project">
    <PageHeader title="Create a Concept" />

    <div v-if="!project" class="layout margins">
      <div v-if="error">
        <div class="title-row">
          <router-link :to="{name: 'projects-list'}"><div class="logo" /></router-link>
          <h1 class="page-title">Something went wrong :/</h1>
        </div>
        Failed to load project: {{error}}
      </div>
      <div v-else>
        Loading project…
      </div>
    </div>

    <div v-if="project" class="layout margins">

      <div class="arrow-container fill">
        <div class="arrow-mask top" ref="topArrowMask" />
        <div class="arrow" ref="positiveArrow" />
        <div class="arrow negative" ref="negativeArrow" />
        <div class="arrow-mask bottom" ref="bottomArrowMask" />
        <div class="arrow-right" ref="modelArrow" />
        <div class="arrow results" ref="resultsArrow">
          <div class="arrow-head top" />
          <div class="arrow-head bottom" />
        </div>
        <div class="arrow-connect" ref="arrowConnect" />
      </div>

      <div class="header">
        <div class="spacer" style="height: 10px;"></div>
        <div class="row">
          <div class="left">
            <span class="cav-name">
              ~<span class="cav-name-input"
                     contenteditable
                     spellcheck="false"
                     @keydown.enter.prevent
                     @blur="project.name = $event.target.innerText.trim()">
                {{ project.name ? project.name : 'untitled-cav' }}
              </span>
            </span>
            <span class="byline"> by {{ project.creatorName ? project.creatorName : 'anon' }}</span>
          </div>
          <div class="spacer" style="flex: 1"></div>
          <div class="row-right">
            <a class="header-button"
                         v-if="cav"
                         :href="cavURL"
                         :download="cavFileName">
              Download .CAV
            </a>
            <span class="header-button disabled" v-else>
              Download .CAV
            </span>
          </div>
        </div>
        <div class="spacer" style="height: 10px;"></div>
        <div class="cav-value-divider">
          <div v-if="project.neuralLens">
            <a
              class="cav-link"
              :href="cavURL"
              :download="cavFileName"
              >
              {{cavValueString}}
            </a>

          </div>
          <div v-else>
          </div>
        </div>
        <div class="spacer" style="height: 12px;"></div>
      </div>


      <div class="seed-area" :class="{empty: positiveEmpty}">
        <div class="seed-header">
          <h2>{{ seedAreaTitle }}</h2>
          <div class="image-count">
            {{project.positiveSet.images.length}}/50+ images
          </div>
        </div>
        <div class="seed-scroll scrollable"
             ref="seedArea"
             @scroll="seedAreaDidScroll">
          <TrainingImageGrid :imageSet="project.positiveSet" ref="positiveSet" />
          <div class="spacer" style="height: 50px;"></div>

          <div ref="negativeHeaderPositionReference">
            <!--
              the negativeHeader position is fixed, so this element is used
              to get the target scroll position
            -->
          </div>
          <h2 ref="negativeHeader" class="sticky">
            <div class="scroll-to-negative-button fill"
                v-if="scrollToNegativeButtonVisible && !positiveEmpty"
                @click="scrollToNegative"></div>
            It is not…
          </h2>
          <TrainingImageGrid :imageSet="project.negativeSet" ref="negativeSet" />
        </div>
      </div>
      <div class="model-area">
        <ModelControl :project="project"
                      ref="modelControl" />
      </div>

      <div class="results-area" :class="{empty: !project.neuralLens}">
        <div class="results-header">
          <SearchSetChooser
            :searchSets="searchSets"
            :selectedSearchSet="selectedSearchSet"
            @didSelectSearchSet="didSelectSearchSet"
            :snapshotId="project.snapshotId"/>
          <h2 style="text-align: right">Concept results</h2>
        </div>
        <div class="results-scroll scrollable"
             @scroll="resultsDidScroll"
             ref="resultsScroller">
          <Results :project="project"
                   :neuralLens="project.neuralLens"
                   :viewMode="viewMode"
                   @didChangeHeight="updateArrows"
                   ref="results" />
        </div>
      </div>
      <ResultsControlBar class="results-controls"
                         :project="project"
                         :viewMode.sync="viewMode" />
    </div>
  </div>
</template>

<script>
import Project from '../model/Project'
import TrainingImageGrid from '@/components/TrainingImageGrid.vue'
import Results from '@/components/Results.vue'
import ModelControl from '@/components/ModelControl.vue'
import SearchSetChooser from '@/components/SearchSetChooser.vue'
import router from '../router'
import projectStorage from '../model/projectStorage'
import cavServer from '@/model/cavServer';
import _ from 'lodash'
import { defaultSearchSet } from '../model/SearchSet'
import PageHeader from '@/components/PageHeader';
import PageFooter from '@/components/PageFooter';
import ResultsControlBar from '@/components/ResultsControlBar';

export default {
  name: 'Project',
  props: ['fromSearchSet'],
  data() {
    return {
      project: null,
      searchSets: [defaultSearchSet],
      error: null,
      viewMode: 'preview',
      scrollToNegativeButtonVisible: true,
      seedAreaTitle: "It is…",
      cav: null,
    }
  },
  mounted() {
    if (!this.$route.params.snapshotId) {
      this.project = new Project();
      this.$nextTick(() => {
        this.updateArrows()
      })
    } else {
      this.load(this.$route.params.snapshotId);
    }

    this.loadSearchSets()

    window.addEventListener('resize', this.windowDidResize);
    window.addEventListener('keydown', this.windowKeydown);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.windowDidResize)
    window.removeEventListener('keydown', this.windowKeydown);
  },
  methods: {
    load(snapshotId) {
      projectStorage.getProjectWithSnapshotId(snapshotId)
        .then(project => {
          this.project = project
          if (this.fromSearchSet) {
            this.didSelectSearchSet(this.fromSearchSet)
            this.fromSearchSet = null
          }
          this.$nextTick(() => {
            this.updateArrows()
          })
          this.downloadCavFile()
        })
        .catch(error => {
          console.error(error)
          this.error = error
        })
    },
    loadSearchSets() {
      projectStorage.getSearchSets()
        .then( sets => {
          this.searchSets = [defaultSearchSet, ...sets]
        })
        .catch(error => {
          console.error(error)
        })
    },
    downloadCavFile() {
      this.cav = null
      if (!this.project.neuralLens) {
        return;
      }
      cavServer.getCAV(this.project.neuralLens.cavID)
        .then(cav => {
          this.cav = cav
        })
    },
    onProjectNameInput(event) {
      this.project.name = _.trim(event.target.innerText)
    },
    didSelectSearchSet(set) {
      this.project.searchSet = set
      this.project.neuralLens = null
      this.viewMode = 'preview'
    },
    scrollToNegative(event) {
      const {negativeHeaderPositionReference, seedArea} = this.$refs;
      const targetScrollPos = negativeHeaderPositionReference.offsetTop - seedArea.offsetTop + 47
      this.$refs.seedArea.scroll({
        top: targetScrollPos,
        behavior: 'smooth'
      })
    },
    seedAreaDidScroll() {
      const {negativeHeaderPositionReference, negativeHeader, seedArea, positiveArrow, negativeArrow} = this.$refs;
      const negativeHeaderIsPinnedToBottom = (
        negativeHeaderPositionReference.offsetTop > negativeHeader.offsetTop
      )
      this.scrollToNegativeButtonVisible = negativeHeaderIsPinnedToBottom

      const targetScrollPos = negativeHeaderPositionReference.offsetTop - seedArea.offsetTop + 30
      if (seedArea.scrollTop > targetScrollPos) {
        this.seedAreaTitle = "It is not…"
      } else {
        this.seedAreaTitle = "It is…"
      }

      this.updateArrows()
    },
    resultsDidScroll() {
      this.updateArrows()
    },
    windowDidResize() {
      this.updateArrows()
    },
    updateArrows() {
      const {
        seedArea,
        topArrowMask,
        bottomArrowMask,
        positiveArrow,
        negativeArrow,
        positiveSet,
        negativeSet,
        modelArrow,
        modelControl,
        resultsArrow,
        results,
        arrowConnect
      } = this.$refs;

      const seedAreaRect = seedArea.getBoundingClientRect()
      topArrowMask.style.height = seedAreaRect.y - 10 + 'px'

      bottomArrowMask.style.top = seedAreaRect.y + seedAreaRect.height + 10 + 'px'
      bottomArrowMask.style.bottom = 0 + 'px'

      const positiveRect = positiveSet.$el.getBoundingClientRect()
      const leftPostion = positiveRect.x + positiveRect.width - 15
      positiveArrow.style.top = positiveRect.y + 'px'
      positiveArrow.style.height = positiveRect.height + 'px'
      positiveArrow.style.left = leftPostion + 'px'

      const negativeRect = negativeSet.$el.getBoundingClientRect()
      negativeArrow.style.top = negativeRect.y - 130 + 'px'
      negativeArrow.style.height = negativeRect.height + 130 + 'px'
      negativeArrow.style.left = leftPostion + 'px'

      const learnButtonRect = modelControl.$refs.learnButton.getBoundingClientRect()
      modelArrow.style.left = leftPostion + 44 + 'px'
      modelArrow.style.top = learnButtonRect.y + 13 + 'px'

      const resultsRect = results.$refs.grid.getBoundingClientRect()
      resultsArrow.style.top = resultsRect.y + 'px'
      resultsArrow.style.left = resultsRect.x - 30 + 'px'
      resultsArrow.style.height = resultsRect.height + 'px'

      const modelRect = modelControl.$el.getBoundingClientRect()
      arrowConnect.style.left = modelRect.x + modelRect.width + 'px'
      arrowConnect.style.width = '28px'
      arrowConnect.style.top = learnButtonRect.y + 19 + 'px'
    },
    windowKeydown(event) {
      if (!this.project.neuralLens) {
        return;
      }

      let handled = true;

      if (event.key == '1') {
        this.viewMode = 'preview'
      } else if (event.key == '2') {
        this.viewMode = 'crop'
      } else if (event.key == '3') {
        this.viewMode = 'inspect-heatmap'
      } else if (event.key == '4') {
        this.viewMode = 'inspect-crop'
      } else {
        handled = false;
      }

      if (handled) {
        event.preventDefault();
        event.stopPropagation();
      }
    },
  },
  computed: {
    cavValueString() {
      if (this.project.neuralLens) {
        return 'CAV: ' + this.project.neuralLens.cavString
      } else {
        return "0".repeat(500)
      }
    },
    cavURL() {
      var blob = new Blob([this.cav], {
        "type": "application/octet-stream"
      });
      return URL.createObjectURL(blob);
    },
    cavFileName() {
      return (this.project.name ? this.project.name : 'untitled') + '.cav'
    },
    selectedSearchSet() {
      if (!this.project) {
         return null
      }

      if (!this.project.searchSet) {
        return defaultSearchSet
      } else {
        return this.project.searchSet
      }
    },
    positiveEmpty() {
      return this.project.positiveSet.images.length === 0
    }
  },
  watch: {
    $route(to, from) {
      let currentSnapshotId = this.project && this.project.snapshotId
      const destSnapshotId = to.params.snapshotId

      if (destSnapshotId !== currentSnapshotId) {
        // see if it's a snapshot in this project, so we don't need to load
        if (this.project) {
          const snapshot = _.find(this.project.snapshots, s => s.snapshotId == destSnapshotId)
          if (snapshot) {
            this.project.loadFromSnapshotJSON(snapshot.json)
            return
          }
        }

        // otherwise, load it from the server
        this.project = null
        this.load(to.params.snapshotId);
      }
    },
    'project.snapshotId': function (snapshotId) {
      if (snapshotId !== this.$route.params.snapshotId) {
        console.log('routing...')
        router.replace({name: 'project-snapshot', params: {snapshotId}})
      }
    },
    'project.positiveSet.images': function(positiveSet){
      this.$nextTick(() => {
        this.updateArrows()
      })
    },
    'project.neuralLens.cavID': function() {
      this.viewMode = 'preview';
      this.downloadCavFile()
      if (this.$refs.resultsScroller) {
        this.$refs.resultsScroller.scrollTop = 0;
      }
    },
    viewMode() {
      this.$nextTick(() => {
        this.updateArrows();
      })
    }
  },
  components: {
    TrainingImageGrid,
    Results,
    ModelControl,
    SearchSetChooser,
    PageHeader,
    PageFooter,
    ResultsControlBar
  }
}
</script>

<style lang="scss" scoped>

.project {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  text-align: left;
  display: flex;
  flex-direction: column;
}
h2 {
  font-weight: bold;
  font-size: 20px;
  padding-top: 12px;
  padding-bottom: 12px;
  margin: 0;
}
.layout {
  display: grid;
  grid-template: "head head head" auto
                 "seed modl resl" 1fr
                 "seed modl resc" auto
                 / 4fr auto 3fr;
  flex: 1;
  min-height: 0;
}

.header {
  grid-area: head;
}
.seed-area {
  grid-area: seed;
  overflow: hidden;
}
.seed-area.empty {
  margin-right: 24px;
}
.seed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-right: 24px;
}
.empty .seed-header {
  margin-right: 0px;
}
.image-count {
  font-weight: 500;
  font-size: 12px;
  color: #7D7D7D;
  letter-spacing: 0.48px;
  text-align: right;
  margin-top: 8px;
}
.sticky {
    position: sticky;
    // -20px offsets the padding on .seed-scroll
    bottom: -20px;
    background: white;;
    z-index: 1;
}
.scroll-to-negative-button {
  cursor: pointer;

  &::after {
    content: "";
    // css triangle
    border-top: 11px solid currentColor;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    position: absolute;
    top: 22px;
    right: 2px;

  }
  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }
}
.seed-scroll {
  height: calc(100% - 47px);
  padding-bottom: 20px;
}
.empty .seed-scroll{
  overflow: hidden;
}
.model-area {
  grid-area: modl;
  height: 100%;
  overflow: hidden;
}
.results-area {
  grid-area: resl;
  overflow: hidden;
  margin-right: -24px
}
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-right: 24px;
}
.results-area > h2 {
  margin-right: 24px;
}
.results-area.empty {
  margin-right: 0px;
}
.results-area.empty > h2 {
  margin-right: 0px;
}
.results-area.empty > .results-header {
  margin-right: 0px;
}
.results-scroll {
  height: calc(100% - 47px);
  padding-bottom: 20px;
}
.empty  > .results-scroll {
  overflow: hidden;
}

// Scroll areas

.seed-scroll, .results-scroll {
  overflow-y: scroll;
  color: rgba(0, 0, 0, 0);
  transition: color .3s ease;

  /* To animate the scrollbar color you need to use the containing element's color */
  &:hover {
    color: rgba(0, 0, 0, 0.3);
  }

  /* Reset children to App's default color */
  & > * {
    color: #454545;
  }

  &::-webkit-scrollbar,
  &::-webkit-scrollbar-thumb {
    width: 26px;
    border-radius: 13px;
    background-clip: padding-box;
    border: 10px solid transparent;
  }
  &::-webkit-scrollbar-track {
    margin-bottom: 20px;
  }
  &::-webkit-scrollbar-thumb {
    box-shadow: inset 0 0 0 10px;
  }
}
.results-scroll {
  &::-webkit-scrollbar-track {
    margin-top: -10px;
    margin-bottom: 10px;
  }
  &::-webkit-scrollbar-thumb {
    width: 26px;
    border-radius: 13px;
    background-clip: padding-box;
  }
}

.results-controls {
  grid-area: resc;
}

.footer {
  grid-area: foot;
}

.row {
  display: flex;
}
.cav-name {
  font-weight: bold;
  font-size: 30px;
  color: #454545;
}
.cav-name-input {
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
  border: none;
  padding-bottom: 5px;
  display: inline-block;
}
.cav-name-input:focus {
  outline: none;
  padding-bottom: 2px;
  border-bottom: 3px solid #3b59ff;
}
.byline {
  padding-left: 10px;
  font-size: 18px;
  color: #B8B8B8;
  font-weight: bold;
}
.cav-value-divider {
  font-family: Roboto, sans-serif;
  font-size: 7px;
  color: #5e5e5e;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.64;

  line-height: 23px;
  // fixed height so that divider height doesn't change when there's no CAV
  height: 23px;
}
.cav-link {
  color: inherit;
  text-decoration: none;
}
.cav-link:hover {
  color: #3B59FF;
}
.line {
  height: 3px;
  background: #d8d8d8;
}
.footer a {
  color: inherit;
}
.positive {
  position: relative;
}
.arrow-container {
  pointer-events: none;
  overflow: hidden;
}
.arrow {
  position: absolute;
  right: 655px;
  border: solid #E8EAED  3px;
  width: 44px;
  border-radius: 16px;
  z-index: -2;
  background-color: white;
}
.arrow.negative {
  border-style: dashed;
  z-index: -3;
}
.arrow.results {
  transform: scaleX(-1);
  position: relative;
}
.arrow::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  bottom: -3px;
  width: calc(50% + 3px);
  background-color: white;
  z-index: -1;
}
.arrow-mask.top {
  position: absolute;
  width: 100%;
  background: white;
  z-index: -1;
  top: 0;
}
.arrow-mask.bottom {
  position: absolute;
  width: 100%;
  background: white;
  z-index: -1;
  bottom: 0;
}
.arrow-right {
  position: absolute;
  left: -200px;
  width: 25px;
  height: 14px;
  z-index: -2;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(../components/assets/arrow_right.svg);
}
.arrow-head {
  position: absolute;
  width: 12px;
  height: 15px;
  left: 14px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(../components/assets/arrow_right_head.svg);
  transform: scale(-1);
  z-index: 0;
}
.arrow-head.top {
  top: -9px;
}
.arrow-head.bottom {
  bottom: -9px;
}
.arrow-connect {
  position: absolute;
  height: 3px;
  background-color: #E8EAED;
  z-index: -2;
}
</style>
