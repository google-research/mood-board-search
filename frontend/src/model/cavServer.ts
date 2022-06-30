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

import {Mutex} from 'async-mutex';
import { CavResult } from '@/model/NeuralLens';
import { ServerTrainingImage, CAVServerImage } from './CAVImage';
import { SEARCH_DATASET } from './ScoutImageDataset';
import _ from 'lodash';
import * as imageUtils from './imageUtils';
import Semaphore from '../../../third_party/Semaphore';

let SERVER_URL = 'http://localhost:8000'


export class CAVServer {
    getAuthMutex = new Mutex()
    uploadSemaphore = new Semaphore(8)

    URLForImage(options: {id: string, userGenerated?: boolean, format?: 'thumbnail'|'jpeg'}) {
        const {id, userGenerated=true, format='thumbnail'} = options;
        const folder = userGenerated ? `${SERVER_URL}/media/cav-content` : `${SERVER_URL}/static-cav-content`

        if (format == 'thumbnail') {
            return `${folder}/${id}.1x.224x224.png`
        } else {
            return `${folder}/${id}.1x.1200x1200.jpg`
        }
    }

    URLForCAV(id: string) {
        return `${SERVER_URL}/media/cavs/${id}.cav`
    }

    async getCAV(id: string): Promise<any> {
        const response = await fetch(this.URLForCAV(id))

        return response.blob()
    }

    async uploadImage(imageURL: string): Promise<CAVServerImage> {
        return this.uploadSemaphore.use(async () => {
            const image = await imageUtils.loadImage(imageURL)

            const exifOrientation = await imageUtils.getEXIFOrientation(image)

            const canvas224 = imageUtils.drawImageToCanvas({image,
                                                            exifOrientation,
                                                            size: {width: 224, height: 224}})
            const canvas1200 = imageUtils.drawImageToCanvas({image,
                                                             exifOrientation,
                                                             size: {width: 1200, height: 1200}})

            const data224 = canvas224.toDataURL("image/png");
            const data1200 = canvas1200.toDataURL("image/jpeg", 0.8);

            const responseJSON = await this.request('/api/upload_image', {
                method: 'post',
                jsonBody: {data224, data1200},
            })

            return CAVServerImage.fromJSON(responseJSON)
        })
    }

    async getImageSet(versionName: string): Promise<ServerTrainingImage[]> {
        const responseJSON = await this.request(`/api/image_set/${versionName}`)
        return responseJSON.images.map((image_json: any) => ServerTrainingImage.fromJSON(image_json))
    }

    async generateCAV(options: {positiveImages: ServerTrainingImage[],
                                negativeImages: ServerTrainingImage[],
                                searchImages?: CAVServerImage[],
                                modelLayer: string}): Promise<CavResult> {

        var json: any = {
            'positive_images': options.positiveImages.map(i => i.toJSON()),
            'negative_images': options.negativeImages.map(i => i.toJSON()),
            'model_layer': options.modelLayer,
        }
        if (options.searchImages) {
            json['search_images'] = options.searchImages.map(i => {
                // search_images uses a special compact JSON encoding
                return {'id': i.id}
            })
            json['search_set'] = 'custom'
        } else {
            json['search_set'] = SEARCH_DATASET
        }
        const response = await this.request('/api/generate_cav', {
            method: 'post',
            jsonBody: json
        })

        return {
            images: response.result_images.map((i: any) => CAVServerImage.fromJSON(i)),
            id: response.cav_id,
            string: response.cav_string,
        }
    }

    async inspectImage(options: {image: CAVServerImage, cavID: string}) {
        return await this.request('/api/inspect', {
            method: 'post',
            jsonBody: {
                'image': options.image.toJSON(),
                'cav_id': options.cavID
            }
        })
    }

    async getImageCrops(options: { image: CAVServerImage; cavId: string; }) {
        const responseJSON = await this.request('/api/crops', {
            method: 'post',
            jsonBody: {
                'image': options.image.toJSON(),
                'cav_id': options.cavId
            }
        })

        return responseJSON as CropsResponse
    }

    private async request(path: string, options: {method?: string, jsonBody?: any} = {}): Promise<any> {
        const {method='get', jsonBody=null} = options

        const response = await fetch(`${SERVER_URL}${path}`, {
             method,
             body: jsonBody ? JSON.stringify(jsonBody) : null,
             headers: {
                 'accept': 'application/json',
                 'content-type': 'application/json',
             },
        })

        if (!response.ok) {
            let errorJson: any = null
            try {
                errorJson = await response.json()
            }
            catch (error) {
                // couldn't get a JSON description of the error, oh well
            }

            if (errorJson && errorJson.detail) {
                throw new Error(`${errorJson.detail} (HTTP ${response.status})`)
            }

            throw new Error(`HTTP error ${response.status} ${response.statusText}`)
        }

        return await response.json()
    }
}

export interface CropSpec {
  x: number,
  y: number,
  width: number,
  height: number,
}

export interface CropsResponse {
    top_crop: CropSpec,
    crops: CropSpec[],
    scores: number[]
}

const cavServer = new CAVServer();
(window as any).cavServer = cavServer;
export default cavServer;
