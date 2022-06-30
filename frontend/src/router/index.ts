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

import Vue from 'vue'
import VueRouter from 'vue-router'
import Project from '../views/Project.vue'
import Publish from '../views/Publish.vue'
import ProjectsList from '../views/ProjectsList.vue'
import NewSearchSet from '../views/NewSearchSet.vue'
import SearchSetPreview from '../views/SearchSetPreview.vue'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'projects-list',
        component: ProjectsList,
    },
    {
        path: '/project/',
        name: 'new-project',
        component: Project,
    },
    {
        path: '/project/:snapshotId',
        name: 'project-snapshot',
        component: Project,
        props: true,
    },
    {
        path: '/project/:snapshotId/publish',
        name: 'publish',
        component: Publish,
    },
    {
        path: '/searchset/',
        name: 'new-search-set',
        component: NewSearchSet,
        props: true,
    },
    {
        path: '/searchset/:searchSetId',
        name: 'search-set',
        component: SearchSetPreview,
        props: true,
    },
]

const router = new VueRouter({
    routes
})

export default router
