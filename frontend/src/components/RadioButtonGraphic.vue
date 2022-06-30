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
  <svg width="18px" height="18px" viewBox="0 0 18 18" version="1.1">
    <circle :stroke="outlineColor" stroke-width="2" fill="none" cx="9" cy="9" r="8"></circle>
    <circle v-if="selected" :fill="blobColor" cx="9" cy="9" r="4"></circle>
  </svg>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'RadioButtonGraphic',
  props: {
    outlineColor: {
      type: String,
      default: 'currentColor'
    },
    blobColor: {
      type: String,
      default: 'currentColor'
    },
    selected: {
      type: Boolean,
      default: true,
    }
  }
})
</script>
