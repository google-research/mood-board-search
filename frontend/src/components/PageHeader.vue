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
  <div class="page-header margins">
    <div class="page-header-row">
      <router-link :to="{name: 'projects-list'}"><div class="logo" /></router-link>
      <h1 class="page-title" :class="titleClass">{{ title }}</h1>
      <div class="spacer" style="flex: 1"></div>
      <div class="right-button" v-for="(button, index) in rightButtons" :key="index">
        <span v-if="typeof button.action === 'function'"
              @click.prevent.stop="button.action()"
              v-text="button.title"
              class="right-button-inner" />
        <router-link v-else
                     :to="button.action"
                     v-text="button.title"
                     class="right-button-inner" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'
import { RawLocation } from 'vue-router'

interface RightButton {
  title: string,
  action: (()=>void) | RawLocation
}

export default {
  name: 'PageHeader',
  props: {
    title: String,
    titleClass: Object,
    rightButtons: {
      default: () => [],
      type: Array as PropType<RightButton[]>
    }
  },
}
</script>

<style lang="scss" scoped>
.page-header {
  color: #454545;
}

.page-header-row {
  display: flex;
  align-items: center;
  margin-bottom: 17px;
  margin-top: 25px;
}

.logo {
  width: 108px;
  height: 34px;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/logo_type.svg);
}

.page-title {
  font-size: 17px;
  margin-bottom: 0;
  margin-left: 15px;

  &.faint {
    color: #b8b8b8;
  }
}

.right-button {
  font-weight: bold;
  font-size: 17px;
  letter-spacing: 0.24px;
  text-align: right;
}
.right-button-inner {
  text-decoration: none;
  cursor: pointer;
  user-select: none;

  &, &:link, &:visited {
    color: inherit;
  }
  &:hover {
    border-bottom: 2px solid currentColor;
  }
}

</style>
