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

import NeuralLens from './NeuralLens'

/**
 * Wrapper class for snapshot JSON, with a few useful properties
 */
export default class ProjectSnapshot {
    constructor (readonly json: any) {}

    get projectId(): string { return this.json.projectId }
    get snapshotId(): string { return this.json.snapshotId }
    get modelLayer(): string { return this.json.modelLayer }
    get date(): number { return this.json.date }

    get neuralLens(): NeuralLensSnapshot|null {
        if (this.json.neuralLens) {
            return new NeuralLensSnapshot(this.json.neuralLens)
        } else {
            return null
        }
    }

    get positiveSetImagesCount(): number { return this.json.positiveSet.images.length }
}

export class NeuralLensSnapshot {
    constructor (readonly json: any) {}

    get snapshotId(): string { return this.json.snapshotId }
}
