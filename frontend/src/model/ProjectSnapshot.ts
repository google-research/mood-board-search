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
