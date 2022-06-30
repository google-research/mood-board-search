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

import { CAVServerImage } from "./CAVImage"

export type ModelLayer = 'mobilenet_12d'|'googlenet_4d'|'googlenet_5b'

export function modelLayerDisplayName(modelLayer: ModelLayer) {
    return {
        mobilenet_12d: 'Mobilenet 12d',
        googlenet_4d: 'Googlenet 4d',
        googlenet_5b: 'Googlenet 5b',
    }[modelLayer]
}

export interface CavResult {
    images: CAVServerImage[],
    id: string,
    string: string,
}

export default class NeuralLens {
    readonly modelLayer: ModelLayer
    readonly snapshotId: string
    readonly resultImages: CAVServerImage[]
    readonly cavString: string
    readonly cavID: string

    constructor(
        options: {modelLayer: ModelLayer,
                  snapshotId: string,
                  resultImages: CAVServerImage[],
                  cavID: string,
                  cavString: string,
                }
    ) {
        this.modelLayer = options.modelLayer
        this.snapshotId = options.snapshotId
        this.resultImages = options.resultImages
        this.cavID = options.cavID
        this.cavString = options.cavString
    }

    static fromJSON(json: any) {
        return new NeuralLens({
            modelLayer: json.modelLayer,
            snapshotId: json.snapshotId,
            resultImages: json.resultImages.map((i: any) => CAVServerImage.fromJSON(i)),
            cavID: json.cavID,
            cavString: json.cavString,
        })
    }

    toJSON() {
        return {
            modelLayer: this.modelLayer,
            snapshotId: this.snapshotId,
            resultImages: this.resultImages.map(i => i.toJSON()),
            cavID: this.cavID,
            cavString: this.cavString,
        }
    }
}
