/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import Vue from 'vue';

export default Vue.extend({
  data() {
    return {
      altKeyDown: false,
    }
  },
  mounted() {
    window.addEventListener('keydown', this.__AltKeyDownMixin__onKeydown)
    window.addEventListener('keyup', this.__AltKeyDownMixin__onKeyup)
    window.addEventListener('blur', this.__AltKeyDownMixin__blur)
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.__AltKeyDownMixin__onKeydown)
    window.removeEventListener('keydown', this.__AltKeyDownMixin__onKeyup)
    window.removeEventListener('blur', this.__AltKeyDownMixin__blur)
  },
  methods: {
    __AltKeyDownMixin__onKeydown(event: KeyboardEvent) {
      if (event.keyCode === 18) {
        this.altKeyDown = true;
      }
    },
    __AltKeyDownMixin__onKeyup(event: KeyboardEvent) {
      if (event.keyCode === 18) {
        this.altKeyDown = false;
      }
    },
    __AltKeyDownMixin__blur(event: FocusEvent) {
      this.altKeyDown = false;
    },
  },
})
