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
  <!-- disable native browser drag-drop behaviour on the whole window -->
  <div id="app"
       @dragover.prevent="$event.dataTransfer.dropEffect = 'none'"
       @dragenter.prevent=""
       @drop.prevent="">
    <router-view />
    <modals-container />
    <v-dialog/>
  </div>
</template>

<script>
export default {
  data() {
    return {
    }
  },
  methods: {
  },
  components: {
  }
}
</script>

<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
@import '../../third_party/hanken-grotesk/stylesheet.css';
@import './styles.scss';

#app {
  height: 100%;
}
</style>
