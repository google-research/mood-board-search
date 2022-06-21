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
