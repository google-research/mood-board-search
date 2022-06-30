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

import { ServerTrainingImage } from './CAVImage'

export default class PublishInfo {
    summary: string = ''
    description: string = ''
    subjectiveQualities: string = ''
    visualQualities: string = ''
    heroImages: {[index: number]: ServerTrainingImage} = {}

    static fromJSON(json: any) {
        const result = new PublishInfo()

        result.summary = json.summary
        result.description = json.description
        result.subjectiveQualities = json.subjectiveQualities
        result.visualQualities = json.visualQualities
        Object.entries(json.heroImages).forEach (([index, image]) =>
            result.heroImages[+index] = ServerTrainingImage.fromJSON(image)
        )

        return result
    }

    toJSON() {
        var jsonHero: {[index: number]: any} = {}
        Object.entries(this.heroImages).forEach (([index, image]) =>
            jsonHero[+index] = image.toJSON()
        )
        return {
            summary: this.summary,
            description: this.description,
            subjectiveQualities: this.subjectiveQualities,
            visualQualities: this.visualQualities,
            heroImages: jsonHero
        }
    }
}
