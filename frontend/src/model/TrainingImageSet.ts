import { CAVTrainingImage, UploadingTrainingImage, ServerTrainingImage } from './CAVImage';
import Project from './Project';
import {Mutex} from 'async-mutex';
import _ from 'lodash';
import scoutImageDataset from './ScoutImageDataset';

export default class TrainingImageSet {
    project: Project
    images: CAVTrainingImage[] = []
    get isPositive() { return true }

    constructor(options: {project: Project}) {
        this.project = options.project;
        this.uploadingImageFinished = this.uploadingImageFinished.bind(this)
    }

    static fromJSON(json: any, project: Project) {
        const imageSet = new this({project})

        imageSet.images = json.images.map((imageJSON: any) => (
            ServerTrainingImage.fromJSON(imageJSON)
        ))

        return imageSet
    }

    get uploadedImages() {
        return this.images.filter(i => !(i instanceof UploadingTrainingImage))
    }

    toJSON() {
        // only persist uploaded images
        const uploadedImages = this.images.filter(i => (i instanceof ServerTrainingImage)) as ServerTrainingImage[]

        return {
            images: uploadedImages.map(i => i.toJSON()),
            imageCount: uploadedImages.length,
        }
    }

    addImageFiles(imageFiles: File[]) {
        const uploadingImages = imageFiles.map(f => (
            new UploadingTrainingImage(f, this.uploadingImageFinished)
        ))

        this.addImages(uploadingImages)
    }

    addImages(images: CAVTrainingImage[], options: {atFront?: boolean} = {}) {
        const {atFront=false} = options

        this.project.trainingDataWillChange()

        if (atFront){
            this.images.unshift(...images)
        } else {
            this.images.push(...images)
        }

        this.project.trainingDataDidChange()
    }

    removeImage(image: CAVTrainingImage) {
        this.project.trainingDataWillChange()

        const index = this.images.indexOf(image)

        if (index === -1) {
            return
        }

        this.images.splice(index, 1)

        this.project.trainingDataDidChange()
    }

    upweightImage(image: CAVTrainingImage) {
        this.project.trainingDataWillChange()
        image.weight = 4
        this.project.trainingDataDidChange()
    }

    downweightImage(image: CAVTrainingImage) {
        this.project.trainingDataWillChange()
        image.weight = 1
        this.project.trainingDataDidChange()
    }

    uploadingImageFinished(uploadingImage: UploadingTrainingImage, serverImage: ServerTrainingImage) {
        // now the image is on the server, swap the UploadingImage for the
        // ServerImage in our dataset.
        const index = this.images.indexOf(uploadingImage)

        if (index === -1) {
            return
        }

        this.images.splice(index, 1, serverImage)

        this.project.trainingDataDidChange()
    }
}

export class NegativeTrainingImageSet extends TrainingImageSet {
    get isPositive() { return false }

    static fromJSON(json: any, project: Project) {
        const imageSet = new this({project})

        imageSet.images = json.images.map((imageJSON: any) => (
            ServerTrainingImage.fromJSON(imageJSON)
        ))

        return imageSet
    }

    async adjustSizeUsingScoutImages(desiredCount: number) {
        // sort user generated at the top. within user-generated, put disabled at the bottom

        if (desiredCount < 0) {
            throw new Error('invalid desired count')
        }

        this.images = _.sortBy(this.images, [
            image => !image.userGenerated,
            image => !image.enabled,
        ])

        const scoutImages = await scoutImageDataset.getNegativeScoutImages()

        let enabledImages;
        while (enabledImages = this.images.filter(i => i.enabled),
               enabledImages.length !== desiredCount) {

            if (enabledImages.length > desiredCount) {
                const lastEnabledImage = _.last(enabledImages)!

                if (lastEnabledImage.userGenerated) {
                    lastEnabledImage.enabled = false;
                } else {
                    // remove it from the array
                    this.images = _.without(this.images, lastEnabledImage)
                }
            }

            if (enabledImages.length < desiredCount) {
                // try to pull scout images that we aren't in the set already
                let candidateScoutImages = scoutImages.filter(i => !this.images.includes(i))

                if (candidateScoutImages.length == 0) {
                    console.warn('run out scout images!')
                    candidateScoutImages = scoutImages.slice()
                }

                this.images.push(_.sample(candidateScoutImages)!)
            }
        }
    }
}
