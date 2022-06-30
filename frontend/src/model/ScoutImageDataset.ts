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

import { Mutex } from 'async-mutex';
import cavServer from './cavServer';
import { ServerTrainingImage } from './CAVImage';

export const NEGATIVE_DATASET = 'negative-v1.1'
export const SEARCH_DATASET = 'search-v2.1'

export class ScoutImageDataset {
    constructor() {}

    _images: ServerTrainingImage[]|null = null
    getMutex = new Mutex()

    async getNegativeScoutImages() {
        return this.getMutex.runExclusive(async () => {
            if (this._images === null) {
                this._images = await cavServer.getImageSet(NEGATIVE_DATASET)
            }
            return this._images;
        });
    }
}

const scoutImageDataset = new ScoutImageDataset()
export default scoutImageDataset;
