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
  <button class="sign-in-with-google-button"
          @click="$emit('click')">
  </button>
</template>

<script>
export default {

}
</script>

<style>
.sign-in-with-google-button {
  width: 191px;
  height: 46px;
  border: none;
  background-image: url(./assets/btn_google_signin_light_normal_web@2x.png);
  background-size: cover;
  background-repeat: no-repeat;
}
.sign-in-with-google-button:focus {
  background-image: url(./assets/btn_google_signin_light_focus_web@2x.png);
  outline: none;
}
.sign-in-with-google-button:active {
  background-image: url(./assets/btn_google_signin_light_pressed_web@2x.png);
}
.sign-in-with-google-button[disabled] {
  background-image: url(./assets/btn_google_signin_light_disabled_web@2x.png);
}
</style>
