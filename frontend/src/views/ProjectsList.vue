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
  <div class="projects-list">

    <PageHeader :title="username"
                :title-class="{faint: true}"
                :right-buttons="[]">
    </PageHeader>

    <div class="margins">
      <div class="title-row">
        <h1>Concept library</h1>
        <router-link :to="{name: 'new-project'}">
          Create a concept →
        </router-link>
      </div>
      <div class="line" />
    </div>

    <main class="margins">
      <div class="tabs">
        <div
          class="tab"
          v-for="section in [featured, inProgress]"
          :key="section"
          @click="selectedSection = section"
          :class="{ selected: section === selectedSection }">
          {{ section }}
        </div>
        <div v-if="loading && projects.length > 0" class="spin-container"><div class="spinner" /></div>
        <div class="spacer" style="flex-grow: 1"/>
        <div class="search-bar" :class="{open: searchOpen}">
          <input
            ref="search"
            type="text"
            name="search"
            placeholder="Search…"
            v-model="searchText"
            class="search-input">
          <div class="search-icon" @click="searchClicked"/>
        </div>
      </div>

      <div class="no-results" v-if="noSearchResults">No results found</div>

      <div class="section" v-if="selectedSection === featured">
        <div class="row">
          <project-card
              v-for="snapshot in filteredPublished"
              :key="snapshot.id"
              :snapshot="snapshot"
              :published="true" />
        </div>
      </div>

      <div class="section"  v-else>
        <div v-if="loading && projects.length == 0" class="loading">Loading…</div>
        <div v-if="error" class="error">
          {{error.toString()}}
          <br>
          <a href="#" @click="getData().catch(console.error)">Try again</a>
        </div>
        <div class="row">
          <project-card
              v-for="project in filteredProjects"
              :key="project.id"
              :snapshot="project.latestSnapshot"
              :user="username"
              :published="false"
              @duplicate="duplicate(project)"
              @deleteProject="deleteProjectClicked(project)" />
        </div>
      </div>
    </main>

    <div class="page-footer-push"></div>
    <PageFooter />
  </div>
</template>

<script>
import projectStorage from '@/model/projectStorage';
import {snapshotDateFormat} from '@/util';
import {modelLayerDisplayName} from '@/model/NeuralLens';
import Project from '@/model/Project';
import PageHeader from '@/components/PageHeader';
import PageFooter from '@/components/PageFooter';
import ProjectCard from '@/components/ProjectCard';
import * as published  from '@/model/published.json'

// Save user's place and cache data as user navigates away and reloads component
var cachedSection = 'Featured'
var cachedProjects = []

export default {
  name: 'ProjectsList',
  data() {
    return {
      username: null,
      projects: cachedProjects,
      published: published.snapshots,
      loading: false,
      error: null,
      selectedSection: cachedSection,
      searchText: '',
      searchOpen: false,
      featured: 'Featured',
      inProgress: 'In-progress',
    }
  },
  mounted() {
    this.loading = true
    this.getData().catch(console.error)
  },
  methods: {
    async duplicate(project) {
      const snapshot = project.latestSnapshot;
      this.loading = true
      this.error = null

      try {
        await projectStorage.copySnapshotToNewProject({
          srcSnapshotId: snapshot.id,
          dstProjectId: Project.generateNewProjectId(),
          dstSnapshotId: Project.generateNewSnapshotId(),
          dstName: snapshot.name + '-copy'
        })
        await this.getData()
      }
      catch (error) {
        this.error = error
      }
      finally {
        this.loading = false
      }
    },
    deleteProjectClicked(project) {
      const snapshot = project.latestSnapshot
      this.$modal.show('dialog', {
        title: "Are you sure you wish to delete ~" + (snapshot.name ? snapshot.name : 'Concept') +"?",
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
              this.deleteProject(project)
              this.$modal.hide('dialog')
            }
          },
        ]
      })
    },
    async deleteProject(project) {
      const snapshot = project.latestSnapshot;
      this.loading = true
      this.error = null

      try {
        await projectStorage.deleteSnapshotWithId(snapshot.id)
        await this.getData()
      }
      catch (error) {
        this.error = error
      }
      finally {
        this.loading = false
      }
    },
    async getData() {
      this.loading = true

      try {
        this.projects = await projectStorage.getUserProjectsSummary()
        this.error = null
      } catch (error) {
        this.error = error
        throw error
      }
      finally {
        this.loading = false
      }
    },
    formatDate(date) {
      return snapshotDateFormat(new Date(date))
    },
    searchClicked() {
      this.searchOpen = !this.searchOpen
    },
    modelLayerDisplayName,
  },
  computed: {
    filteredProjects: function() {
      if (this.searchText === '') {
        return this.projects
      } else {
        return _.filter(this.projects, project => {
          const snapshot = project.latestSnapshot
          const name = snapshot.name ? snapshot.name : 'Concept'
          const description = snapshot.publishInfo ? snapshot.publishInfo.subjectiveQualities : ''
          var text = name + project.latestSnapshot.creatorName + description
          return text.toLowerCase().includes(this.searchText.toLowerCase())
        })
      }
    },
    filteredPublished: function() {
      if (this.searchText === '') {
        return this.published
      } else {
        return _.filter(this.published, snapshot => {
          var text = snapshot.name + snapshot.publishInfo.subjectiveQualities + snapshot.creatorName
          return text.toLowerCase().includes(this.searchText.toLowerCase())
        })
      }
    },
    noSearchResults: function() {
      if (!this.searchOpen) {
        return false
      }

      if (this.selectedSection === this.featured) {
        return this.filteredPublished.length === 0
      }

      if (this.selectedSection === this.inProgress) {
        if (this.loading) {
          return false
        }
        return this.filteredProjects.length === 0
      }
    }
  },
  watch: {
    selectedSection: function() {
      cachedSection = this.selectedSection
    },
    projects: function() {
      cachedProjects = this.projects
    },
    searchOpen: function() {
      if (this.searchOpen) {
        this.$refs.search.focus()
      } else {
        this.searchText = ''
      }
    },
  },
  components: {
    PageHeader,
    PageFooter,
    ProjectCard,
  }
}
</script>

<style>
  .right-button {
    font-weight: 400;
    font-size: 12px !important;
    color: #5B5B5B;
    letter-spacing: 0.2px;
    color: #B4B9C1;
    margin-bottom: -5px;
  }
  .page-header-row .spacer {
    flex: unset !important;
    width: 10px;
  }
</style>
<style scoped lang="scss">
.projects-list {
  text-align: left;

  display: flex;
  flex-direction: column;
  min-height: 100%;
}
.title-row {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  a {
    font-weight: 700;
    font-size: 17px;
    color: #454545;
    letter-spacing: 0.24px;
    text-align: right;
    text-decoration: none;
  }
}
h1 {
  font-size: 30px;
  color: #454545;
  letter-spacing: 0.43px;
  margin-bottom: 10px;
}
.line {
  height: 3px;
  background: #EEEEEE;
  margin: 10px 0;
}
.margins {
  min-width: unset;
}
main {
  $card: 320px;
  $edge: 40px;
  position: relative;
  margin: 0px auto;
  width: $card - $edge;
  @media (min-width: ($card * 2) + $edge) {
    width: ($card * 2) - $edge;
  }
  @media (min-width: ($card * 3) + $edge) {
    width: ($card * 3) - $edge;
  }
  @media (min-width: ($card * 4) + $edge) {
    width: ($card * 4) - $edge;
  }
  @media (min-width: ($card * 5) + $edge) {
    width: ($card * 5) - $edge;
  }
}
.error {
  color: #f7afca;
  a, :link {
    color: inherit;
  }
}
.tabs {
  display: flex;
  align-items: center;
}
.tab {
  font-weight: 500;
  font-size: 16px;
  color: #6F747B;
  letter-spacing: 0.23px;
  text-align: center;
  cursor: pointer;
  margin-right: 30px;
  white-space: nowrap;
}
.tab.selected {
  color: #454545;
  text-decoration: underline;
}
.section {
  margin-left: -20px;
  margin-right: -20px;
}
.row {
  display: flex;
  flex-wrap: wrap;
}
.spin-container {
  position: relative;
}
.spinner {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}
@keyframes spinner {
  to {transform: rotate(360deg);}
}
.spinner:before {
  content: '';
  box-sizing: border-box;
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  margin-top: -8px;
  margin-left: -8px;
  border-radius: 50%;
  border: 2px solid #ccc;
  border-top-color: transparent;
  animation: spinner .8s linear infinite;
}
.search-icon {
  position: absolute;
  right: 5px;
  top: 5px;
  width: 28px;
  height: 28px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(../components/assets/icon_search.svg);
  cursor: pointer;
}
.open .search-icon {
  background-image: url(../components/assets/icon_search_close.svg);
}
.search-bar {
  position: relative;
}
.search-input {
  background: #FFFFFF;
  border: none;
  border-bottom: 2px solid #E8EAED;

  height: 38px;
  width: 30px;

  font-family: "Hanken Grotesk", Roboto, sans-serif;
  color: #454545;
  font-weight: 500;
  font-size: 16px;
  letter-spacing: 0.23px;

  padding-right: 40px;
  transition: all ease 0.15s;
  opacity: 0;
  pointer-events: none;
}
.open .search-input {
  border-bottom: 2px solid #E8EAED;
  width: 200px;
  opacity: 1;
  pointer-events: unset;
}
.open .search-input:focus {
  border-bottom: 2px solid #454545;
}
.search-input::placeholder {
  opacity: 0.5;
  color: #454545;
}
.no-results, .loading {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  font-weight: 500;
  font-size: 16px;
  color: #6F747B;
  letter-spacing: 0.23px;
  text-align: center;
  opacity: 0.5;
}
</style>
