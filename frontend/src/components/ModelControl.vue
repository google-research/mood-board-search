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
  <div class="model-control">
    <div style="height: 47px; flex-shrink: 0;" />
    <div class="spacer" style="flex: 1"></div>
    <div class="model-control-box"
         :class="{ 'model-select-open': modelSelectOpen }">
      <div class="top-row"  @click="disclosureClicked">
        <div class="icon-cavstudio" />
        <div class="model-name" v-if="selectedModel != undefined">Model: {{ selectedModel.name }}</div>
        <div style="flex-grow: 1" />
        <div class="disclosure"/>
      </div>
      <div class="model-select-container">
        <div class="model-select">
          <div class="model-description">{{ selectedModel.description }}</div>
          <div class="model-select-row">
            <div class="model-select-item"
                 v-for="model in models"
                 :key="model.name"
                 @click="modelClicked(model)">
              <RadioButtonGraphic outlineColor="#d9d9d9"
                                  blobColor="#3c59ff"
                                  :selected="selectedModel === model" />
              {{ model.name }}
            </div>
          </div>
        </div>
      </div>
      <div class="learn-button"
           :class="lensButtonState"
           @click="learnClicked"
           ref="learnButton">
        Learn Concept
        <div class="spinner" />
      </div>

      <div class="error" v-if="project.neuralLensErrorDescription">{{ project.neuralLensErrorDescription }}</div>

      <div class="snapshot-container">
        <router-link v-for="snapshot in project.snapshots"
                     :key="snapshot.snapshotId"
                     :to="{name: 'project-snapshot', params: {snapshotId: snapshot.snapshotId}}"
                     class="snapshot-link">
          <div class="snapshot-row"
               :class="{ visible: snapshot.snapshotId === project.snapshotId,
                         fresh: currentLensUpToDateWithSnapshot(snapshot),
                         published: snapshot.snapshotId == project.publishedSnapshotId, }">
              <div class="active-dot" />
              <div class="summary">
                <span class="line">
                  <span v-if="currentLensUpToDateWithSnapshot(snapshot)">
                    {{ modelLayerDisplayName(snapshot.modelLayer) }} + {{ snapshot.positiveSetImagesCount }} seeds
                  </span>
                  <span v-else>
                    Waiting to run...
                  </span>
                </span>
              </div>
              <div class="date">{{ format(snapshot.date) }}</div>
          </div>
        </router-link>
      </div>
    </div>

    <div class="spacer" style="flex: 3"></div>
    <div class="footer">
      by <a href="https://nordprojects.co/" target="_blank">Nord Projects</a>
      and <br><a href="https://research.google/teams/brain/" target="_blank">Google Brain</a>
      and <a href="https://research.google/teams/mural/" target="_blank">Mural</a>
      teams at Google
    </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { snapshotDateFormat } from '@/util';
import NeuralLens, {modelLayerDisplayName} from '../model/NeuralLens';
import _ from 'lodash'
import Project from '../model/Project';
import router from '../router'
import RadioButtonGraphic from './RadioButtonGraphic';

const models = [
  {
    id: 'mobilenet_12d',
    name: 'Mobilenet 12d',
    description: 'A simpler model that’s good at detecting more obvious visual themes like colour and texture.',
  },
  {
    id: 'googlenet_4d',
    name: 'Googlenet 4d',
    description: 'A model that’s good at detecting distinct visual elements like shapes and patterns.',
  },
  {
    id: 'googlenet_5b',
    name: 'Googlenet 5b',
    description: 'A more conceptual model that’s good at detecting diverse patterns, textures and compositions.',
  },
]

export default Vue.extend({
  name: 'ModelControl',
  props: {
    project: Project,
  },
  data() {
    return {
      modelSelectOpen: false,
    }
  },
  mounted() {
  },
  computed: {
    models() {
      return models
    },
    selectedModel() {
      return _.find(this.models, { id: this.project.modelLayer });
    },
    lensButtonState() {
      // 'enabled' | 'disabled' | 'loading'
      if (this.project.isLearning) {
        return 'loading'
      } else {
        return this.project.canLearnLens ? 'enabled' : 'disabled'
      }
    }
  },
  methods: {
    modelLayerDisplayName,
    disclosureClicked() {
      this.modelSelectOpen = !this.modelSelectOpen
    },
    modelClicked(model) {
      this.project.modelLayer = model.id
    },
    learnClicked() {
      this.project.learnNeuralLens()
    },
    currentLensUpToDateWithSnapshot(snapshot) {
      if (!snapshot.neuralLens) { return false }
      return (snapshot.snapshotId === snapshot.neuralLens.snapshotId)
    },
    format(date) {
      return snapshotDateFormat(new Date(date))
    },
  },
  components: {
    RadioButtonGraphic,
  }
})
</script>

<style scoped lang="scss">
.model-control {
  width: 280px;
  margin-left: 35px;
  margin-right: 55px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
}
.model-control-box {
  background: #FFFFFF;
  border: 3px solid #EEEEEE;
  border-radius: 12px;
  box-sizing: border-box;
  overflow: hidden;

  text-align: center;
}
.top-row {
  display: flex;
  align-items: center;
  margin-top: 12px;
  margin-left: 15px;
  margin-right: 15px;
  cursor: pointer;
}
.icon-cavstudio {
  width: 26px;
  height: 26px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/icon_cavstudio.svg);
}
.disclosure {
  width: 30px;
  height: 30px;
  margin-right: -10px;
  cursor: pointer;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/icon_disclosure.svg);
  transition: all ease 0.15s;
}
.model-select-open .disclosure {
  transform: rotate(-90deg)
}
.model-name {
  font-weight: 700;
  font-size: 12px;
  color: #454545;
  letter-spacing: 0.17px;
  margin-left: 11px;
}
.model-select-container {
  height: 0px;
  overflow: hidden;
  transition: all ease 0.25s;
}
.model-select-open .model-select-container {
  height: 118px;
}
.model-select {
  padding: 15px;
}
.model-description {
  font-family: Roboto, sans-serif;
  font-size: 11px;
  color: #5E5E5E;
  letter-spacing: 0.44px;
  line-height: 16px;
  text-align: left;
  height: 50px;
  overflow: hidden;
}
.model-select-row {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}
.model-select-item {
  font-weight: 500;
  font-size: 9px;
  color: #777777;
  letter-spacing: 0.36px;
  text-align: center;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.learn-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 22px auto;

  padding-left: 19px;
  padding-right: 19px;
  height: 38px;
  border-radius: 22.5px;
  background: #3B59FF;
  cursor: pointer;

  font-weight: 500;
  font-size: 15px;
  color: #FFFFFF;
  letter-spacing: 0.21px;
}
.learn-button.disabled {
  background: #EEEEEE;
  cursor: unset;
  pointer-events: none;
}
.learn-button.loading {
  background: #00FFC6;
  cursor: unset;
  pointer-events: none;
}
.spinner {
  display: none;
  width: 22px;
  height: 22px;
  margin-left: 10px;
}
.loading .spinner {
  display: inline-block;
}
.spinner:after {
  content: " ";
  display: block;
  width: 14px;
  height: 14px;
  margin: 0px;
  border-radius: 50%;
  border: 4px solid #fff;
  border-color: #fff transparent #fff transparent;
  animation: spinner 1.2s linear infinite;
}
@keyframes spinner{
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.error {
  color: #f7afca;
  font-size: 12px;
  margin-bottom: 20px;
}


.snapshot-container {
  max-height: 239px;
  border-top: 2px solid #f8f8f8;
  overflow-y: auto;
}

.snapshot-link {
  text-decoration: none;
  display: block;
}
.snapshot-row {
  display: flex;
  align-items: center;
  padding-left: 11px;
  padding-right: 14px;
  min-height: 28px;
  cursor: pointer;
}
.snapshot-link:nth-last-child(odd) {
  background-color: #F8F8F8;
}
.active-dot {
  background: #e8eaed;
  width: 9px;
  height: 9px;
  border-radius: 4.5px;
  opacity: 0;
  transition: all ease 0.15s;
  margin-left: 4px;
  margin-right: 3px;

  flex-shrink: 0;
  flex-grow: 0;

  .visible & {
    opacity: 1;
  }
  .fresh & {
    background: #00FFC6;
  }
  .published & {
    opacity: 1;
    width: 16px;
    height: 16px;
    margin: 0;
    background: url(./assets/published_icon.svg)
  }
  .published.visible & {
    background: url(./assets/published_icon_green.svg)
  }
}

.summary {
  font-weight: 500;
  font-size: 10px;
  color: #7D7D7D;
  letter-spacing: 0.4px;
  line-height: 21px;
  margin-left: 8px;
  text-align: left;
  white-space: nowrap;
}
.line {
  display: inline-block;
}
.date {
  font-weight: 400;
  font-size: 10px;
  color: #7D7D7D;
  letter-spacing: 0.4px;
  text-align: right;
  line-height: 21px;
  flex-grow: 1;
  margin-left: 10px;
}

.footer {
  font-weight: 500;
  font-size: 11px;
  color: #BDC1C6;
  text-align: center;
  line-height: 20px;
  margin: 7px 0;

  a, a:link, a:visited {
    color: inherit;
  }

}

</style>
