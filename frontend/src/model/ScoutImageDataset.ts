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
