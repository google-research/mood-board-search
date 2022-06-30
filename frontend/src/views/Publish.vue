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
  <div class="publish">
    <PageHeader title="Publish" />

    <div class="margins">
      <div class="spacer" style="height: 10px"></div>

      <router-link :to="{name: 'project-snapshot',
                         params: {snapshotId: $route.params.snapshotId}}"
                   class="header-button">
        ← Studio
      </router-link>

      <div v-if="!project">
        <div class="spacer" style="height: 10px"></div>
        <div v-if="error">
          Failed to load project: {{error}}
        </div>
        <div v-else>
          Loading…
        </div>
      </div>
    </div>

    <div v-if="project" class="layout">

      <div class="margins">
        <div class="publish-margins">

          <div class="spacer" style="height: 50px"></div>

          <h2>Name your Concept</h2>
          <div class="spacer" style="height: 10px"></div>
          <span class="cav-name">
            ~<span class="cav-name-input"
                   contenteditable
                   spellcheck="false"
                   @keydown.enter.prevent
                   @blur="project.name = $event.target.innerText.trim()">{{ project.name ? project.name : 'untitled-cav' }}</span>
          </span>

          <div class="spacer" style="height: 50px"></div>

          <h2>Choose hero images</h2>
          <p class="field-description">
            Of the images you’ve used to train your Concept, choose the ones that best communicate it to others
          </p>

          <publish-hero-grid :project="project"/>

          <div class="spacer" style="height: 80px"></div>

        </div>
      </div>

      <div class="info-bg">
        <div class="margins">
          <div class="publish-margins">
            <div class="spacer" style="height: 70px"></div>

            <h2>Capture your perspective in a sentence.</h2>
            <div class="spacer" style="height: 20px"></div>

            <div class="text-box-container">
              <textarea class="text-box"
                        v-model="project.publishInfo.summary"
                        @blur="save" />
              <div class="character-limit"
                   :class="characterLimitClass(project.publishInfo.summary, 180)"
                   v-text="characterLimitContent(project.publishInfo.summary, 180)" />
            </div>

            <div class="spacer" style="height: 100px"></div>

            <h2>Describe your perspective</h2>
            <div class="spacer" style="height: 10px"></div>

            <p class="field-description">
              What unique point of view on the world are you trying to instill in your Concept? What are you drawn to? What interests you? How is this reflected in your work?
            </p>

            <div class="spacer" style="height: 10px"></div>

            <div class="text-box-container">
              <textarea class="text-box"
                        v-model="project.publishInfo.description"
                        @blur="save" />
              <div class="character-limit"
                   :class="characterLimitClass(project.publishInfo.description, 600)"
                   v-text="characterLimitContent(project.publishInfo.description, 600)" />
            </div>

            <div class="spacer" style="height: 100px"></div>

            <div class="row">
              <div class="column">

                <h2>What are the subjective qualities of your images?</h2>
                <p class="field-description">
                  E.g. The feeling, state, style, sentiment, encounter or action you’re trying to embody in your curated images…
                </p>

                <div class="text-box-container">
                  <textarea class="text-box"
                            v-model="project.publishInfo.subjectiveQualities"
                            @blur="save" />
                  <div class="character-limit"
                       :class="characterLimitClass(project.publishInfo.subjectiveQualities, 140)"
                       v-text="characterLimitContent(project.publishInfo.subjectiveQualities, 140)" />
                </div>

              </div>

              <div class="column spacer" style="flex: 0; flex-basis: 10%"></div>

              <div class="column">

                <h2>What are the visual qualities of your images?</h2>
                <p class="field-description">
                  E.g. Composition, colour, shape, object, texture. Should be consistently present across your image set…
                </p>

                <div class="text-box-container">
                  <textarea class="text-box"
                            v-model="project.publishInfo.visualQualities"
                            @blur="save" />
                  <div class="character-limit"
                       :class="characterLimitClass(project.publishInfo.visualQualities, 140)"
                       v-text="characterLimitContent(project.publishInfo.visualQualities, 140)" />
                </div>
              </div>
            </div>

            <div class="spacer" style="height: 100px"></div>
          </div>
        </div>
      </div>

      <div class="spacer" style="height: 50px"></div>

      <center>
        <div v-if="!isPublishing">

          <button class="publish-button"
                  v-if="!isPublished"
                  @click="publishButtonClicked">
            Publish Concept
          </button>

          <div class="publish-info" v-if="isPublished" style="margin-bottom: 20px">
            This snapshot is already published!
          </div>

          <button class="un publish-button"
                  v-if="isPublished"
                  @click="unpublishButtonClicked">
            Unpublish Concept
          </button>

          <div class="publish-info error" v-if="publishingError">{{publishingError}}</div>

          <div class="spacer" style="height: 10px"></div>
          <div class="publish-info" v-if="!isPublished">
            Saves your Concept to the cloud so <br>
            that other people can use it.
          </div>
        </div>
      </center>

    </div>

    <div class="spacer" style="height: 70px"></div>

    <div class="page-footer-push"></div>
    <PageFooter />
  </div>
</template>

<script>
import projectStorage from '../model/projectStorage';
import PublishHeroGrid from '../components/PublishHeroGrid';
import PageHeader from '@/components/PageHeader';
import PageFooter from '@/components/PageFooter';

export default {
  name: 'Publish',
  data() {
    return {
      project: null,
      error: null,
      isPublishing: false,
      publishingError: null,
    }
  },
  mounted() {
    this.load(this.$route.params.snapshotId)
  },
  computed: {
    isPublished() {
      if (!this.project) return false
      return this.project.snapshotId === this.project.publishedSnapshotId
    }
  },
  methods: {
    async load(snapshotId) {
      projectStorage.getProjectWithSnapshotId(snapshotId)
        .then(project => {
          this.project = project
        })
        .catch(error => {
          console.error(error)
          this.error = error
        })
    },
    save() {
      this.project.setNeedsSave()
    },
    onTextBoxKeyDown(event) {
      const textBox = event.target
      if (!textBox.dataset.maxLength) return;

      const characterLimit = parseInt(textBox.dataset.maxLength)

      const currentLength = textBox.value.length
    },
    publishButtonClicked() {
      this.publishSnapshot(this.project.snapshotId)
    },
    unpublishButtonClicked() {
      this.publishSnapshot(null)
    },
    publishSnapshot(snapshotId) {
      this.isPublishing = true
      projectStorage.publishSnapshot(this.project.projectId, snapshotId).then(() => {
        this.$router.push({
          name: 'project-snapshot',
          params: {snapshotId: this.project.snapshotId}
        })
      })
      .catch(error => {
        console.error(error);
        this.publishingError = error
      })
      .finally(() => {
        this.isPublishing = false
      })
    },
    characterLimitClass(text, maxLength) {
      return {
        error: text.length > maxLength,
        warning: (text.length <= maxLength) && (text.length > maxLength - 10),
      }
    },
    characterLimitContent(text, maxLength) {
      return `${text.length}/${maxLength}`
    }
  },
  watch: {
    $route(to, from) {
      const destSnapshotId = to.params.snapshotId

      this.load(destSnapshotId);
    },
  },
  components: {
    PublishHeroGrid,
    PageHeader,
    PageFooter,
  },
}
</script>

<style lang="scss" scoped>

.publish {
  text-align: left;
  font-size: 16px;
  font-weight: 500;

  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.publish-margins {
  max-width: 940px;
  margin: 0 auto;
}

h2 {
  font-weight: 500;
  font-size: 18px;
  color: #3B59FF;
  margin-bottom: 2px;
}

input, textarea {
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
  resize: none;
}
textarea {
  width: 100%;
}
.cav-name {
  font-weight: bold;
  font-size: 30px;
  color: #454545;
  background: #dbfff7;
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
}

.info-bg {
  background: #fafafa;
}

.field-description {
  font-weight: 500;
  font-size: 16px;
  color: #A8A8A8;
  line-height: 28px;
  max-width: 660px;;
}

.text-box-container {
  background: white;
  padding: 18px 16px;
  padding-bottom: 12px;

  &:focus-within {
    outline: 2px solid #3B59FF;
  }
}
.text-box {
  min-height: 115px;
  border: none;
  color: #555555;
  &:focus {
    outline: none;
  }
}

.character-limit {
  font-size: 14px;
  color: #A8A8A8;
  .text-box-container:focus-within &.warning {
    color: #ffc290;
  }
  &.error {
    color: #fd88a1;
  }
}

.row {
  display: flex;
}
.column {
  flex: 1
}

.publish-info {
  font-family: "Roboto Mono", monospace;
  font-size: 11px;
  color: #C4C4C4;
  letter-spacing: 0.16px;
  text-align: center;
  line-height: 20px;
}

.publish-button {
  line-height: 38px;
  background: #3B59FF;
  border-radius: 19px;
  padding: 0 22px;
  color: white;
  display: inline-block;
  font-weight: 500;
  border: none;
  cursor: pointer;

  font-size: 15px;

  &.un {
    background: #FF3B3B;
  }

  &:focus {
    outline: none;
  }
}

.error {
  color: #f7afca;
}

</style>
