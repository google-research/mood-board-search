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
  <div class="container" :class="{disabled,
                                  'inspect-mode-active': inspectModeActive,
                                  'alt-down': altKeyDown}">
    <transition name="slide-up">
      <div class="inspect-settings-drawer"
           v-if="inspectModeActive">
        <div class="inspect-settings">
          <div class="spacer" style="flex: 1"></div>
          <button class="inspect-button"
                  @click.prevent.stop="buttonClicked('inspect-heatmap')">
            <RadioButtonGraphic class="radio" :selected="viewMode == 'inspect-heatmap'" />
            Heatmap
          </button>
          <div class="spacer" style="flex: 1"></div>
          <button class="inspect-button"
                  @click.prevent.stop="buttonClicked('inspect-crop')">
            <RadioButtonGraphic class="radio" :selected="viewMode == 'inspect-crop'" />
            Focus
          </button>
          <div class="spacer" style="flex: 1"></div>
          <div class="info-tooltip"
               v-tooltip="{
                 content: `
                   <strong>Choose images to view through the machine’s eyes</strong><br>
                   Heatmap: visualise CAV score by image segments<br>
                   Focus: part of the image the CAV is most attracted to
                 `,
                 offset: 10,
                 autoHide: false,
               }">
            <img svg-inline src="./assets/i_button.svg" >
          </div>
        </div>
      </div>
    </transition>
    <div class="results-control-bar"
         :class="{'inspect-mode': inspectModeActive}">
      <button class="view-mode-button preview"
              :class="{selected: viewMode == 'preview'}"
              @click.prevent.stop="buttonClicked('preview')">
        Preview
      </button>
      <div class="divider"></div>
      <button class="view-mode-button"
              :class="{selected: viewMode == 'crop'}"
              @click.prevent.stop="buttonClicked('crop')"
              v-tooltip="{content: `<strong>Results cropped by the CAV for optimum composition</strong><br>
                                    Tip: hold alt ⌥ to toggle mode on/off`,
                          delay: {show: 1500, hide: 300},
                          offset: 3}">
        AI crop
      </button>
      <div class="divider"></div>
      <button class="view-mode-button"
              :class="{selected: inspectModeActive}"
              @click.prevent.stop="buttonClicked('inspect')"
              v-tooltip="{content: `<strong>Understand why the CAV is choosing images</strong><br>
                                    Tip: hold alt ⌥ to toggle mode on/off`,
                          delay: {show: 1500, hide: 300},
                          offset: 3}">
        Inspect
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import Vue, {PropType} from 'vue'
import Project from '@/model/Project';
import RadioButtonGraphic from '@/components/RadioButtonGraphic.vue';
import AltKeyDownMixin from './mixins/AltKeyDownMixin';

export default Vue.extend({
  name: 'ResultsControlBar',
  mixins: [AltKeyDownMixin],
  data() {
    return {
      previousInspectMode: 'inspect-heatmap',
    }
  },
  props: {
    project: Object as PropType<Project>,
    viewMode: String,
  },
  methods: {
    buttonClicked(buttonName: string) {
      if (this.disabled) { return }

      if (buttonName == 'preview') {
        this.$emit('update:viewMode', 'preview')

      } else if (buttonName == 'crop') {
        this.$emit('update:viewMode', 'crop')

      } else if (buttonName == 'inspect') {
        this.$emit('update:viewMode', this.previousInspectMode)

      } else if (buttonName == 'inspect-heatmap') {
        this.$emit('update:viewMode', 'inspect-heatmap')
        this.previousInspectMode = 'inspect-heatmap'

      } else if (buttonName == 'inspect-crop') {
        this.$emit('update:viewMode', 'inspect-crop')
        this.previousInspectMode = 'inspect-crop'

      } else {
        throw new Error('unknown button')
      }
    },
  },
  computed: {
    disabled() {
      return this.project.neuralLens == null;
    },
    inspectModeActive() {
      return this.viewMode.startsWith('inspect')
    },
  },
  components: {
    RadioButtonGraphic,
  }
})
</script>

<style lang="scss" scoped>
.container {
  // hardcoded height to let scrolling content slide behind the radius
  height: 23px;
  position: relative;

  &.inspect-mode-active {
    height: 66px;
  }
}
.results-control-bar {
  position: absolute;
  bottom: 0;
  left: -10px;
  right: -10px;
  height: 35px;
  background: #FFFFFF;
  box-shadow: 0 0 25px -12px rgba(0,0,0,0.79);
  border-radius: 12px 12px 0 0;
  overflow: hidden;

  display: flex;
}
.view-mode-button {
  flex: 1;

  background: transparent;
  border: none;
  font-family: inherit;
  cursor: button;

  font-weight: 500;
  font-size: 12px;
  color: #7B8FFF;
  background: white;

  // note: holding 'alt' makes it look like 'preview' is selected, regardless
  // of viewMode.

  &.selected, .alt-down &.preview {
    color: #ffffff;
    background: #7B8FFF;
  }

  .alt-down & {
    &.selected:not(.preview) {
      color: rgb(208, 212, 216);
      background: white;
      cursor: default;
    }
  }

  .disabled &, .alt-down.disabled & {
    color: rgb(208, 212, 216);
    background: white;
    cursor: default;
  }
}
.divider {
  flex-basis: 1px;
  background: #f2f3f6;
}

.inspect-settings-drawer {
  position: absolute;
  bottom: 23px;
  left: 0;
  right: 0;
  height: 45px;
  background: #E0E5FF;
  color: #5972FF;
  box-shadow: 0 0 30px -15px rgba(0,0,0,0.50);
  border-radius: 12px 12px 0 0;
  overflow: hidden;

  .alt-down & {
    background: #fff;
    color: #ccc;
  }
}
.slide-up-enter-active {
  transition: height 0.20s ease;
}
.slide-up-leave-active {
  transition: height 0.20s ease;
}
.slide-up-enter, .slide-up-leave-to {
  height: 0;
}
.inspect-settings {
  height: 33px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 10px;
}
.inspect-button {
  font-weight: 500;
  font-size: 11px;

  .radio {
    vertical-align: -40%;
    margin-right: 5px;
  }
}
.info-tooltip {
  display: block;
  font-size: 0;
  svg {
    display: block;
    margin-bottom: 2px;
    &:focus {
      outline: none;
    }
  }
  &:hover {
    color: #0e3a2f;
  }
}
</style>
