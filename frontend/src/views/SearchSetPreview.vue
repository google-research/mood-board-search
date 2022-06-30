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
    <PageHeader title="Search sets"
                :right-buttons="[
                  {
                    title: 'Done →',
                    action: (fromSnapshotId
                             ? {name: 'project-snapshot',
                                params: {snapshotId: fromSnapshotId, fromSearchSet: searchSet}}
                             : {name: 'projects-list'})
                  }
                ]" />

    <div class="margins">
      <div v-if="!searchSet">
        <div class="spacer" style="height: 10px"></div>
        <div v-if="error">
          Failed to load search set: {{error}}
        </div>
        <div v-else>
          Loading…
        </div>
      </div>
    </div>

    <div v-if="searchSet">
      <div class="margins">
        <div class="line"/>

        <div class="preview" :key="searchSet.searchSetId">
            <div class="button-error" :style="{visibility: buttonError ? 'visible' : 'hidden' }">
              {{ buttonError ? buttonError.toString() : 'none' }}
            </div>
            <div class="preview-hint">
              Name your search set
            </div>

            <div class="preview-name">
              <span class="set-name-input"
                     :contenteditable="true"
                     spellcheck="false"
                     @keydown.enter.prevent
                     @blur="searchSet.name = $event.target.innerText.trim()">{{ searchSet.name ? searchSet.name : 'untitled-search-set' }}</span>
            </div>
            <div class="preview-author" v-if="searchSet.creatorName">by {{ searchSet.creatorName }}</div>

            <div class="preview-count">{{ searchSet.images.length }} images </div>
            <div class="grid">
              <div class="image"
                v-for="(image, index) in searchSet.images.slice(0, 18)"
                :key="index"
                :style="{backgroundImage: `url('${image.url({format: 'thumbnail'})}')`}" />
              <div class="grid-fade" v-if="searchSet.images.length > 18" />
            </div>

            <button class="studio-button delete"
                 @click="deleteClicked">
              Remove search set
            </button>
        </div>
      </div>
    </div>

    <div class="spacer" style="height: 70px"></div>
    <div class="page-footer-push"></div>

    <PageFooter />
  </div>
</template>

<script>
import projectStorage from '../model/projectStorage';
import {CustomSearchSet} from '../model/SearchSet';
import router from '../router';
import PageHeader from '@/components/PageHeader.vue';
import PageFooter from '@/components/PageFooter.vue';
import { defaultSearchSet } from '../model/SearchSet'


export default {
  name: 'SearchSetPreview',
  props: [ 'fromSnapshotId' ],
  data() {
    return {
      searchSet: null,
      error: null,
      buttonError: null,
      url: null
    }
  },
  mounted() {
    this.loadUser()
    this.url = window.location.href
  },
  methods: {
    load(searchSetId) {
      projectStorage.getSearchSetWithId(searchSetId)
        .then(searchSet => {
          this.searchSet = searchSet
        })
        .catch(error => {
          console.error(error)
          this.error = error
        })
    },
    deleteClicked() {
      this.buttonError = null
      this.$modal.show('dialog', {
        title: "Are you sure you wish to remove<br> ‘" + this.searchSet.name + "’ from your search set list?",
        text: 'This action cannot be undone.',
        buttons: [
          {
            title: 'Cancel',
          },
          {
            title: 'Delete',
            class: 'destructive',
            default: true,
            handler: () => {
              this.deleteSearchSet()
            }
          },
        ]
      })
    },
    deleteSearchSet() {
      console.log('delete')
      projectStorage.deleteSearchSetWithId(this.searchSet.searchSetId)
        .then(() => {
          if (this.fromSnapshotId) {
            router.push({name: 'project-snapshot', params: {snapshotId: this.fromSnapshotId, fromSearchSet: defaultSearchSet}})

          } else {
            router.push({name: 'projects-list'})
          }
          this.$modal.hide('dialog')
        })
        .catch(error => {
          console.error(error)
          this.$modal.hide('dialog')
          this.buttonError = error
        })
    },
  },
  watch: {
    $route: {
      immediate: true,
      handler(to) {
        this.load(to.params.searchSetId)
      }
    }
  },
  components: {
    PageHeader,
    PageFooter,
  }
}
</script>

<style scoped lang="scss">
.spacer {
  flex-grow: 1;
}
.line {
  background-color: #EEEEEE;
  height: 3px;
}
.search-set {
  text-align: left;
  font-size: 16px;
  font-weight: 500;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.preview {
  text-align: center;
  position: relative;
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
.set-name-input {
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
  border: none;
  padding-bottom: 5px;
  display: inline-block;
}
.set-name-input:focus {
  outline: none;
  padding-bottom: 2px;
  border-bottom: 3px solid #3b59ff;
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
  bottom: -30px;
  background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, #FFFFFF 87%);
  height: 230px;
}

.buttons {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
}
.import {
  margin-top: 28px;
}
.studio-button.delete {
  background-color: #E8EAED;
  color: #454545;
  margin-top: 30px;
  &:active {
      background-color: #b8babc;
  }
}
.button-error {
  color: #FF005E;
  opacity: 0.5;
  font-size: 11px;
  line-height: 40px;
}
.share {
  font-weight: 500;
  font-size: 12px;
  color: #7D7D7D;
  letter-spacing: 0.48px;
  text-align: center;
  line-height: 21px;
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>
