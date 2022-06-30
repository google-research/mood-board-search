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
  <div class="search-set">
    <PageHeader title="/ Search sets" />

    <div class="margins">
      <!-- <div class="header">
        <div class="title-row">
          <router-link :to="{name: 'projects-list'}"><div class="logo" /></router-link>
          <h1 class="page-title">New search set</h1>
        </div>
      </div> -->

      <div class="spacer" style="height: 10px"></div>

      <router-link
        v-if="fromSnapshotId"
        :to="{name: 'project-snapshot', params: {snapshotId: fromSnapshotId}}"
        class="header-button">
        ← Studio
      </router-link>
      <router-link
        v-else
        :to="{name: 'projects-list'}"
        class="header-button">
        ← Studio
      </router-link>

    </div>

    <div v-if="searchSet">
      <div class="margins">
        <div class="spacer" style="height: 20px"></div>
        <div class="line"/>
        <div class="spacer" style="height: 40px"></div>

        <div class="row">
          <div class="scratch">
            <h2>New search set</h2>
            <div class="placeholder">
              <!-- Upload -->
              <div class="upload-area fill"
                ref="upload"
                :class="{dragging: numImagesDragging > 0}"
                @dragenter="dragHandler.dragenter($event)"
                @dragover="dragHandler.dragover($event)"
                @dragleave="dragHandler.dragleave($event)"
                @drop="dragHandler.drop($event)">

                <!-- Uploading empty state -->
                <div v-if="!isInUploadingMode" class="area fill">
                  <div class="spacer" style="height: 92px"/>
                  <div class="message">
                    Drag and drop your own images to create a new search set
                  </div>
                  <div class="tips">
                    <span style="font-weight: 500">Tips</span><br>
                    Aim for 2000-3000 images<br>
                    You are responsible for the images you upload. Make sure you have the right to use them.
                  </div>
                </div>

                <!-- Uploading -->
                <div v-else class="area fill">
                  <div style="height: 130px" />
                  <div class="progress">
                    <div class="progress-bar" :style="progressStyle" />
                  </div>

                  <template v-if="uploadingImageCount > 0">
                    <div class="message">
                      Uploading {{ uploadingImageCount }} images…
                    </div>

                    <div class="spacer" style="flex: 1"></div>

                    <div class="area-subtitle" :class="{hide: searchSet.isUploaded}">
                      <span class="blue">Important!</span><br>
                      Leave your computer on with this page open until it’s finished calculating activations.
                    </div>
                  </template>

                  <template v-else-if="erroredImages.length > 0">
                    <div class="message">
                        Uploaded {{ searchSet.images.length }} images.
                    </div>

                    <div class="spacer" style="flex: 1"></div>

                    <div class="area-subtitle">
                      <span class="error">
                        {{ erroredImages.length }} image{{ erroredImages.length == 1 ? '' : 's' }} failed to upload
                        <img svg-inline class="icon" src="../components/assets/i_button.svg" alt="info-icon"
                             style="width: 12px; height: 12px"
                             v-tooltip.bottom-start="{
                               content: failedImagesTooltipContent,
                               offset: 3,
                             }" />
                      </span>
                    </div>

                    <div class="spacer" style="flex: 2"></div>

                    <div class="button-row">
                      <button class="studio-button" @click="retryUploadButtonPressed">Try again</button>
                      <button class="studio-button" @click="continueButtonPressed">Ignore and continue</button>
                    </div>
                  </template>

                  <template v-else>
                    <div class="message">
                        Upload successful!
                    </div>

                    <div class="spacer" style="flex: 1"></div>

                    <div class="button-row">
                      <button class="studio-button" @click="continueButtonPressed">Continue</button>
                    </div>
                  </template>

                  <div style="height: 30px" />

                  <div class="save-error" v-if="saveError">
                    {{ saveError }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Import is disabled for local CAVstudio -->
          <div v-if="false" class="import" :class="{hide: isInUploadingMode}">
            <h2>From elsewhere</h2>
            <div class="placeholder">
              <div class="import-area area fill">
                <div class="spacer" style="height: 92px"/>
                <div class="message">
                  Import a search set someone else has made
                </div>
                <input
                  type="text"
                  class="url-input"
                  placeholder="paste search set URL"
                  v-model="importUrl"
                  v-on:keyup.enter="importClicked"/>
                <button class="studio-button"
                     :class="{disabled: !importUrl, active: importing}"
                     @click="importClicked">
                  Import
                </button>
                <div class="import-error" v-if="importError">{{ importError }}</div>
                <div class="tips">
                  <span style="font-weight: 500">Where do I find the URL?</span><br>
                  Ask the search set creator to ‘Open’ their search set. They’ll see a URL they can copy and share.
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>

    <div class="spacer" style="height: 70px"></div>

    <div class="page-footer-push"></div>

    <PageFooter />
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import projectStorage from '../model/projectStorage';
import {CustomSearchSet} from '../model/SearchSet';
import ImageDragHandler from '@/components/ImageDragHandler';
import router from '../router'
import cavServer from '../model/cavServer';
import PageHeader from '@/components/PageHeader.vue';
import PageFooter from '@/components/PageFooter.vue';
import { Route } from 'vue-router';

interface ErroredImage {
  file: File
  error: Error
}

export default Vue.extend({
  name: 'NewSearchSet',
  props: [ 'fromSnapshotId' ],
  data() {
    return {
      searchSet: new CustomSearchSet(),
      isSaving: false,
      saveError: null as Error|null,
      dragHandler: null as ImageDragHandler|null,
      uploadingImageCount: 0,
      erroredImages: [] as ErroredImage[],
      importUrl: null as string|null,
      importError: null as Error|null,
      importing: false,
    }
  },
  mounted() {
    const uploadElement = this.$refs.upload as Element;
    this.dragHandler = new ImageDragHandler(uploadElement, imageFiles => {
      for (const imageFile of imageFiles) {
        this.uploadImageFile(imageFile)
      }
    });
    window.addEventListener('beforeunload', this.onBeforeUnload);
  },
  beforeDestroy() {
    window.removeEventListener('beforeunload', this.onBeforeUnload);
  },
  computed: {
    numImagesDragging(): number {
      return this.dragHandler?.imagesAboutToDrop ?? 0
    },
    progressStyle(): Object {
      const done = this.searchSet.images.length
      var progress = done / this.totalDroppedImageCount

      return {
        width: progress * 100 + '%'
      }
    },
    totalDroppedImageCount(): number {
      const uploading = this.uploadingImageCount
      const errored = this.erroredImages.length
      const done = this.searchSet.images.length

      return uploading + errored + done
    },
    isInUploadingMode(): boolean {
      return this.totalDroppedImageCount > 0
    },
    failedImagesTooltipContent(): string {
      const failedFilenames = this.erroredImages.map(i => i.file.name)
      return `Failed images: \n${failedFilenames.join(', ')}`
    }
  },
  methods: {
    uploadImageFile(imageFile: File) {
      let blobURL: string;

      try {
        blobURL = URL.createObjectURL(imageFile)
      }
      catch (error) {
        this.erroredImages.push({file: imageFile, error})
        return
      }

      this.uploadingImageCount += 1

      cavServer.uploadImage(blobURL)
        .then(serverImage => {
          this.searchSet.images.push(serverImage)
        })
        .catch(error => {
          console.error('image upload failed', error)
          this.erroredImages.push({file: imageFile, error})
        })
        .finally(() => {
          this.uploadingImageCount -= 1
          URL.revokeObjectURL(blobURL)

          if (this.uploadingImageCount == 0) {
            this.searchSet.save()
          }
        })
    },
    continueButtonPressed() {
      this.isSaving = true;
      this.saveError = null

      this.searchSet.save()
        .then(() => {
          router.push({
            name: 'search-set',
            params: {searchSetId: this.searchSet.searchSetId, fromSnapshotId: this.fromSnapshotId},
          })
        })
        .catch(error => {
          this.saveError = error
        })
        .finally(() => {
          this.isSaving = false
        })
    },
    retryUploadButtonPressed() {
      const imageFiles = this.erroredImages.map(i => i.file)
      this.erroredImages = []

      for (const imageFile of imageFiles) {
        this.uploadImageFile(imageFile)
      }
    },
    onBeforeUnload(event: BeforeUnloadEvent) {
      if (this.isInUploadingMode) {
        event.returnValue = 'Your images will not upload if you leave now.'
      }
    },
    async importClicked() {
      this.importError = null
      if(!this.importUrl) return;
      this.importing = true

      var parser = document.createElement('a');
      parser.href = this.importUrl

      try {
        // parse the input URL
        const path = parser.hash.split('#')[1]
        if (!path) {
          throw new Error('Cannot find search set in URL')
        }

        const route: Route = (this.$router as any).matcher.match(path)
        const importId = route.params.searchSetId

        if (!importId) {
          throw new Error('Cannot find search set in URL')
        }

        // download, copy and save the new search set
        const importSearchSet = await projectStorage.getSearchSetWithId(importId)

        var newSet = importSearchSet.createCopy()
        await newSet.save()

        router.push({
          name: 'search-set',
          params: {searchSetId: newSet.searchSetId, fromSnapshotId: this.fromSnapshotId }
        })
      }
      catch(error) {
        console.error(error)
        this.importError = error
      }
      finally {
        this.importing = false
      }
    },
  },
  components: {
    PageHeader,
    PageFooter,
  },
})
</script>

<style scoped lang="scss">
.search-set {
  text-align: left;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
.line {
  background-color: #EEEEEE;
  height: 3px;
}
.row {
  display: flex;
  justify-content: space-around;
}
.scratch {
  max-width: 410px;
  flex-grow: 1;
  margin-right: 20px;
  margin-left: 20px;
}
.import {
  max-width: 410px;
  flex-grow: 1;
  margin-left: 20px;
  margin-right: 20px;
}
h2 {
  text-align: center;
  font-weight: 700;
  font-size: 20px;
  color: #454545;
  letter-spacing: 0.29px;
}
.area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 30px;
}
.upload-area.dragging::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  background: rgba(59,89,255,0.05);
  border: 3px solid #3B59FF;
  border-radius: 8px;
}
.placeholder {
  position: relative;
  width: 100%;
  height: 410px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}
.message {
  max-width: 267px;
  font-weight: 700;
  font-size: 20px;
  color: #454545;
  letter-spacing: 0.29px;
  text-shadow: 0 0 10px #FFFFFF;
}
.tips {
  font-family: Roboto, sans-serif;
  font-weight: 400;
  font-size: 12px;
  color: #454545;
  letter-spacing: 0.17px;
  text-align: center;
}
.upload-area {
  align-items: center;
  justify-content: center;
}
.area-subtitle {
  margin-top: 5px;
  font-weight: 500;
  font-size: 13px;
  color: #454545;
  letter-spacing: 0.19px;
  text-align: center;
  line-height: 20px;
  text-shadow: 0 0 10px #FFFFFF;
}
.area-subtitle span.blue {
  color: #3B59FF;
}
.url-input {
  background: #FFFFFF;
  border: 2px solid #E8EAED;
  border-radius: 23px;
  height: 46px;
  width: 78%;
  font-weight: 500;
  font-size: 13px;
  color: #454545;
  letter-spacing: 0.19px;
  text-shadow: 0 0 10px #FFFFFF;
  padding-right: 21px;
  padding-left: 21px;
  user-select: none;
  transition: all ease 0.15s;
}
.url-input:focus {
  border: 3px solid #3B59FF;
  padding-right: 20px;
  padding-left: 20px;
}
.url-input::placeholder {
  opacity: 0.5;
  color: #454545;
}
.import-error {
  color: #FF005E;
  opacity: 0.8;
  font-family: Roboto, sans-serif;
  font-weight: 500;
  font-size: 12px;
}
.progress {
  margin-bottom: 20px;
  overflow: hidden;
  height: 8px;
  width: 100%;
  background: white;
  position: relative;
}
.progress-bar {
  position: absolute;
  background: #3B59FF;
  top: 0;
  left: 0;
  bottom: 0;
  transition: all ease-out 0.15s;
}
.button-row {
  text-align: center;

  * {
    margin: 0 10px;
  }
  :first-child {
    margin-left: 0;
  }
  :last-child {
    margin-right: 0;
  }
}

.save-error {
  color: #f7afca;
  font-size: 12px;
}
.hide {
  opacity: 0;
  transition: opacity ease 0.15s;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
.preview {
  text-align: center;
  position: relative;
  overflow: hidden;
  max-height: 550px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-auto-rows: 1fr;
  gap: 10px;
  position: relative;
  margin-top: -10px;
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
.image {
  cursor: pointer;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.preview-hint {
  font-weight: 700;
  font-size: 20px;
  color: #454545;
  letter-spacing: 0.29px;
}
.preview-name {
  font-weight: 500;
  font-size: 22px;
  color: #454545;
  letter-spacing: 0.31px;
  text-shadow: 0 0 10px #FFFFFF;
  margin-top: 30px;
}
.preview-author {
  font-weight: 700;
  font-size: 16px;
  color: #B8B8B8;
  letter-spacing: 0.23px;
  margin-top: 30px;
}
.preview-count {
  font-weight: 500;
  font-size: 12px;
  color: #7D7D7D;
  letter-spacing: 0.48px;
  text-align: left;
  line-height: 21px;
  margin-top: -10px;
  margin-bottom: 18px;
}
.grid-fade {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, #FFFFFF 87%);
  height: 230px;
}
</style>
