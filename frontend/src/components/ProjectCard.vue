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
  <div class="card" :class="{published: published}">
    <router-link :to="{name: 'project-snapshot', params: {snapshotId: snapshot.id }}">
      <div class="corners fill">
        <div class="menu-button" @click.prevent="openContextMenu" />
        <div
          class="hero"
          v-if="heroImages || published">
          <div
            v-for="(image, index) in heroImages"
            :key="index"
            class="hero-image">
            <div
              v-if="image"
              class="image fill"
              :style="{backgroundImage: `url('${image.url({format: 'jpeg'})}')`}" />
            <div
              v-else
              class="hero-placeholder fill" >
            </div>
          </div>
        </div>
        <div class="placeholder" v-else>
          <div class="icon-lens" />
        </div>
        <div class="name">
          ~{{ snapshot.name ? snapshot.name : 'Concept' }}
        </div>
        <div class="author">
          by {{ user === snapshot.creatorName ? 'you' : snapshot.creatorName }}
        </div>
        <div class="qualities" :class="{ none: !qualities }">
          {{ qualities ? qualities : 'No qualities listed yet.' }}
        </div>
        <div class="bottom-row" v-if="published">
          <div class="location">
            <div class="globe" />
            {{ snapshot.publishInfo.location }}
          </div>
          <button class="try-button" @click.stop="navigateToProject">
            Try Concept
          </button>
        </div>
        <div class="bottom-row" v-else>
          <div class="date">
            {{ formatDate(snapshot.date) }}
          </div>
          <div class="arrow">
            →
          </div>
        </div>
      </div>
    </router-link>

    <VueContext ref="menu" :lazy="true" @open="selected=true" @close="selected=false">
      <li v-if="!published">
        <a href="#"
           @click.prevent="duplicate">Duplicate concept</a>
      </li>
      <li>
        <a href="#"
           @click.prevent="copyURL">Copy concept URL</a>
      </li>
      <li v-if="!published">
        <a href="#"
           class="destructive"
           @click.prevent="deleteProject">Delete concept</a>
      </li>
    </VueContext>

  </div>
</template>

<script>
import {projectDateFormat} from '@/util';
import { ServerTrainingImage } from '@/model/CAVImage';
import { VueContext } from 'vue-context';

export default {
  name: 'ProjectCard',
  props: ['snapshot', 'user', 'published'],
  methods: {
    formatDate(date) {
      return projectDateFormat(new Date(date))
    },
    openContextMenu(event) {
      this.$refs.menu.open(event)
    },
    duplicate() {
      this.$emit('duplicate', this.snapshot)
    },
    copyURL() {
      var path = this.$router.resolve({name: 'project-snapshot', params: {snapshotId: this.snapshot.id}}).href
      var origin = window.location.href.split('#')[0]
      var fullUrl = origin + path
      navigator.clipboard.writeText(fullUrl)
    },
    deleteProject() {
      this.$emit('deleteProject')
    },
    navigateToProject() {
      this.$router.push({name: 'project-snapshot', params: {snapshotId: this.snapshot.id}})
    }
  },
  computed: {
    heroImages() {
      // If concept has hero images in published info
      if (this.snapshot.publishInfo && this.snapshot.publishInfo.heroImages)  {
        const heroImages = this.snapshot.publishInfo.heroImages
        if (heroImages[0] && heroImages[1] && heroImages[2]) {
          const count = this.published ? 6 : 3
          return _.range(count).map(index =>
            heroImages[index] ? ServerTrainingImage.fromJSON(heroImages[index]) : null
          )
        }
      }

      // If no hero images use top images from training set
      if (this.snapshot.topImages && this.snapshot.topImages.length > 0) {
        const topImages = this.snapshot.topImages
        return _.range(3).map(index => {
          if (topImages.length > index) {
            return ServerTrainingImage.fromJSON(topImages[index])
          } else {
            // Repeat top image for single image concepts
            return ServerTrainingImage.fromJSON(topImages[0])
          }
        })
      }
      return null
    },
    qualities() {
      if (!this.snapshot.publishInfo) {
        return null
      }
      return this.snapshot.publishInfo.subjectiveQualities
    },
  },
  components: {
    VueContext,
  },
}
</script>

<style scoped lang="scss">
  .card {
    background: #FFFFFF;
    box-shadow: 0 2px 45px -20px rgba(63,63,63,0.50);
    border-radius: 13px;
    width: 282px;
    height: 304px;
    margin: 19px;
    position: relative;
  }
  .card.published {
    height: 487px;
  }
  .corners {
    border-radius: 13px;
    overflow: hidden;
  }
  .placeholder {
    height: 188px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-image: url(./assets/project_placeholder.png);
  }
  .icon-lens {
    width: 44px;
    height: 44px;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-image: url(./assets/icon_lens_white.svg);
    opacity: 0.8;
  }
  .hero {
    height: 188px;
    position: relative;
    background: #EEEEEE;
  }
  .published .hero {
    height: 282px;
  }
  .hero-image {
    position: absolute;
  }
  .image {
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }
  .hero-placeholder {
    background: #EEEEEE;
  }
  .hero-image {
    width: 94px;
    height: 94px;
  }
  .hero-image:nth-child(1)  {
    width: 188px;
    height: 188px;
  }
  .hero-image:nth-child(2)  {
    right: 0;
  }
  .hero-image:nth-child(3)  {
    top: 94px;
    right: 0;
  }
  .hero-image:nth-child(4)  {
    top: 188px;
  }
  .hero-image:nth-child(5) {
    top: 188px;
    left: 94px;
  }
  .hero-image:nth-child(6)  {
    top: 188px;
    right: 0;
  }
  .name, .author, .qualities, .date, .location {
    margin-left: 19px;
    margin-right: 19px;
  }
  .name {
    font-weight: 700;
    font-size: 19px;
    color: #454545;
    letter-spacing: 0.19px;
    margin-top: 15px;
  }
  .author {
    font-weight: 500;
    font-size: 13px;
    color: #71767F;
    letter-spacing: 0.2px;
    margin-top: 4px;
  }
  .qualities {
    font-weight: 500;
    font-size: 13px;
    color: #5B5B5B;
    letter-spacing: 0.2px;
    line-height: 19px;
    margin-top: 4px;
    height: 57px;
  }
  .qualities.none {
    color: #B4B9C1;
    display: none;
  }
  .date {
    font-weight: 500;
    font-size: 12px;
    color: #71767F;
    letter-spacing: 0.18px;
  }
  .arrow {
    font-weight: 700;
    font-size: 22px;
    color: #4A4A4A;
    letter-spacing: 0.31px;
    margin-right: 20px;
  }
  a {
    text-decoration: none;
    color: inherit;
  }
  .bottom-row {
    margin-top: 17px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .published .bottom-row {
    margin-top: 22px;
  }
  .menu-button {
    position: absolute;
    top: 11px;
    right: 11px;
    width: 21px;
    height: 21px;
    opacity: 0;
    cursor: pointer;
    background-position: center;
    background-repeat: no-repeat;
    background-image: url(./assets/icon_menu.svg);
    transition: all ease 0.15s;
    z-index: 100;
  }
  .corners:hover .menu-button {
    opacity: 1;
  }
  .location {
    font-weight: 500;
    font-size: 11px;
    color: #71767F;
    letter-spacing: 0.17px;
    display: flex;
    align-items: center;
  }
  .globe {
    width: 18px;
    height: 18px;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-image: url(./assets/icon_globe.svg);
    display: inline-block;
    margin-right: 5px;
    margin-top: -2px;
  }
  .try-button {
    font-family: "Hanken Grotesk", Roboto, sans-serif;
    font-weight: 500;
    font-size: 14px;
    color: #454545;
    letter-spacing: 0.2px;
    text-align: center;
    height: 35px;
    width: 114px;
    border: 2px solid #454545;
    border-radius: 19px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 22px;
  }
  .try-button:hover {
    background: #454545;
    color:  #FFFFFF;
  }
  .try-button:active, .try-button:focus {
    background: #71767F;
    color:  #FFFFFF;
    border: 2px solid #71767F;
  }
</style>
