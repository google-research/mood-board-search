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

module.exports = {
    pages: {
        index: {
            entry: 'src/main.ts',
            template: 'public/index-template.html',
            filename: 'index.html',
            title: 'CAVstudio'
        },
    },
    pluginOptions: {
        webpackBundleAnalyzer: {
            openAnalyzer: false,
            reportFilename: '/tmp/webpack-bundle-report.html',
        }
    },
    chainWebpack: config => {
        config.module
            .rule("vue")
            .use("vue-svg-inline-loader")
                .loader("vue-svg-inline-loader")
                .options({ /* ... */ });
    }
}
