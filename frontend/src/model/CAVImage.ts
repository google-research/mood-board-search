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

import cavServer from './cavServer'
import * as uuid from "uuid";

type CAVImageURLFormat = 'thumbnail'|'jpeg'

/**
 * Base image interface
 */
export interface CAVImage {
    readonly isUploading?: boolean
    readonly userGenerated: boolean
    url(options?: {format?: CAVImageURLFormat}): string
}

/**
 * An image that can be used to train a CAV.
 */
export interface CAVTrainingImage extends CAVImage {
    weight: number
    enabled: boolean
}

/**
 * An image that's stored on the backend CAV server.
 */
export class CAVServerImage implements CAVImage {
    vueKey: string
    userGenerated: boolean

    constructor(readonly id: string, options: {userGenerated?: boolean} = {}) {
        const {userGenerated=false} = options
        this.userGenerated = userGenerated
        this.vueKey = uuid.v4()
    }

    static fromJSON(json: any) {
        return new CAVServerImage(json.id, {userGenerated: json.user_generated})
    }

    toJSON() {
        return {
            id: this.id,
            user_generated: this.userGenerated,
        }
    }

    url(options: {format?: CAVImageURLFormat} = {}): string {
        const {format='thumbnail'} = options

        return cavServer.URLForImage({
            id: this.id,
            userGenerated: this.userGenerated,
            format,
        })
    }
}

/**
 * A training image that's stored on the backend CAV server.
 */
export class ServerTrainingImage extends CAVServerImage implements CAVTrainingImage {
    weight = 1
    enabled = true

    static fromJSON(json: any) {
        if (!json.id) {
            throw new Error('failed to deserialize ServerTrainingImage from '+JSON.stringify(json))
        }

        const image = new ServerTrainingImage(json.id, {userGenerated: json.user_generated})

        image.enabled = json.enabled ?? true
        image.weight = json.weight ?? 1

        return image
    }

    toJSON() {
        return {
            id: this.id,
            weight: this.weight,
            enabled: this.enabled,
            user_generated: this.userGenerated,
        }
    }
}

/**
 * A training image that's still local, waiting to upload.
 */
export class UploadingTrainingImage implements CAVTrainingImage {
    _isUploading = false
    get isUploading() { return this._isUploading }
    get userGenerated() { return true }
    weight = 1
    enabled = true

    blobURL: string
    errorDescription: string|null = null

    constructor(
        readonly file: File,
        readonly onComplete: (uploadingImage: UploadingTrainingImage, result: ServerTrainingImage)=>void
    ) {
        this.blobURL = URL.createObjectURL(file)

        this.tryUpload()
    }

    dispose() {
        URL.revokeObjectURL(this.blobURL)
    }

    url(): string {
        return this.blobURL
    }

    tryUpload() {
        if (this._isUploading) return;
        this._isUploading = true

        this.upload().then(serverImage => {
            this._isUploading = false
            this.errorDescription = ''
            this.onComplete(this, serverImage)
        }).catch(error => {
            this._isUploading = false
            this.errorDescription = `Image upload failed. ${error}`
            console.error('image upload failed', error)
        })
    }

    async upload(): Promise<ServerTrainingImage> {
        const serverImage = await cavServer.uploadImage(this.blobURL)

        const trainingImage = new ServerTrainingImage(serverImage.id, {userGenerated: serverImage.userGenerated})
        trainingImage.weight = this.weight

        return trainingImage
    }
}
