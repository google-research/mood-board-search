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
  <div class="page-footer margins">
    <div class="line" />
    <div class="text">
      by <a href="https://nordprojects.co/" target="_blank">Nord Projects</a>
      and <a href="https://research.google/teams/brain/" target="_blank">Google Brain</a>
      and <a href="https://research.google/teams/mural/" target="_blank">Mural</a>
      teams at Google.
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageFooter',
}
</script>

<style lang="scss">
// put your footer in a flex column and put one of these before it to push the
// footer to the bottom of the window.
.page-footer-push {
  flex-basis: 0;
  flex-grow: 1;
}
</style>

<style lang="scss" scoped>
.page-footer {
  font-family: 'Roboto Mono', monospace, sans-serif;
  font-weight: 500;
  font-size: 11px;
  color: #858585;
  background: white;
  letter-spacing: 0.16px;
  text-align: center;
  line-height: 46px;
  margin-top: 15px;

  .line {
    height: 3px;
    background: #eeeeee;
  }
  .text {
    padding-top: 0px;;
  }
  a {
    color: inherit;
  }
}
</style>
