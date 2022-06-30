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

import ResizeObserver from 'resize-observer-polyfill'
import Vue from 'vue';

export default Vue.extend({
    data() {
        return {
            elementSize: {width: 0, height: 0},
            __ObserveSizeMixin__observer: null as ResizeObserver|null,
        }
    },
    mounted() {
        this.__ObserveSizeMixin__update()
        this.__ObserveSizeMixin__observer = new ResizeObserver(entries => {
            this.__ObserveSizeMixin__update()
        })
        this.__ObserveSizeMixin__observer.observe(this.$el);
    },
    beforeDestroy() {
        this.__ObserveSizeMixin__observer?.disconnect()
    },
    methods: {
        __ObserveSizeMixin__update() {
            this.elementSize.width = this.$el.clientWidth;
            this.elementSize.height = this.$el.clientHeight;
        }
    },
})
