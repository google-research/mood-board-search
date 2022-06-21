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
