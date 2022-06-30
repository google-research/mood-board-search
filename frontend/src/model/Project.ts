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

import TrainingImageSet, { NegativeTrainingImageSet } from './TrainingImageSet'
import {makeRandomId, delay} from '@/util'
import { ModelLayer } from './NeuralLens'
import NeuralLens from './NeuralLens'
import projectStorage from './projectStorage';
import _ from 'lodash'
import cavServer from './cavServer'
import ProjectSnapshot from './ProjectSnapshot';
import PublishInfo from './PublishInfo';
import {SearchSet, defaultSearchSet} from './SearchSet';
import { ServerTrainingImage } from './CAVImage';

export default class Project {
    projectId: string
    // the snapshot ID that will be used by the project during the _next_ save.
    // also determines the URL of the page.
    snapshotId: string
    positiveSet: TrainingImageSet
    negativeSet: NegativeTrainingImageSet

    neuralLens: NeuralLens|null = null
    neuralLensErrorDescription: string|null = null
    isLearning = false

    revisionNumber = 0

    creatorName: string|null|undefined = null

    publishInfo = new PublishInfo()
    publishedSnapshotId: string|null = null

    private _name: string|null = null
    get name() { return this._name }
    set name(value) {
        if (value !== this._name) {
            this._name = value
            this.setNeedsSave()
        }
    }

    private _modelLayer: ModelLayer
    get modelLayer() { return this._modelLayer }
    set modelLayer(value) {
        if (value !== this._modelLayer) {
            this.trainingDataWillChange()
            this._modelLayer = value
            this.trainingDataDidChange()
        }
    }

    private _searchSet: SearchSet = defaultSearchSet
    get searchSet() { return this._searchSet }
    set searchSet(value) {
        if (value === this._searchSet) return;
        this.trainingDataWillChange()
        this._searchSet = value
        this.trainingDataDidChange()
    }

    constructor(options?: {snapshotId: string, snapshots: ProjectSnapshot[], publishedSnapshotId: string|null}) {
        this.positiveSet = new TrainingImageSet({project: this})
        this.negativeSet = new NegativeTrainingImageSet({project: this})
        this._modelLayer = 'googlenet_4d'
        this.creatorName = 'you'

        if (options) {
            const {snapshotId, snapshots, publishedSnapshotId} = options
            const snapshot = _.find(snapshots, s => s.snapshotId === snapshotId)

            if (!snapshot) {
                throw new Error('Failed to create project - snapshot not found in `snapshots`')
            }

            this.projectId = snapshot.projectId
            this.snapshotId = snapshot.snapshotId
            this.snapshots = snapshots
            this.publishedSnapshotId = publishedSnapshotId
            this.loadFromSnapshotJSON(snapshot.json)
        } else {
            this.projectId = Project.generateNewProjectId()
            this.snapshotId = Project.generateNewSnapshotId()
        }
    }

    learnNeuralLens() {
        if (this.isLearning) return
        this.isLearning = true
        this.neuralLensErrorDescription = null

        cavServer.generateCAV({
            positiveImages: this.positiveSet.images as ServerTrainingImage[],
            negativeImages: this.negativeSet.images as ServerTrainingImage[],
            searchImages: this.searchSet?.images ?? undefined,
            modelLayer: this.modelLayer,
        }).then(result => {
            this.trainingDataWillChange()
            this.neuralLens = new NeuralLens({
                modelLayer: this.modelLayer,
                snapshotId: this.snapshotId,
                resultImages: result.images,
                cavID: result.id,
                cavString: result.string,
            })
            this.trainingDataDidChange()
            this.isLearning = false
        }).catch(error => {
            console.error(error)
            this.neuralLensErrorDescription = `Learning failed. ${error}`;
            this.isLearning = false
        });
    }

    get canLearnLens() {
        const imageCount = this.positiveSet.images.length
        const uploadedCount = this.positiveSet.uploadedImages.length
        return imageCount > 0 && uploadedCount === imageCount
    }

    ///////////////
    // Callbacks //
    ///////////////

    trainingDataWillChange() {
        if (this.neuralLens && this.snapshotId === this.neuralLens.snapshotId) {
            // changing the training set makes the neural lens out-of-date.
            // increment the snapshot ID so these edits comprise a new
            // snapshot.
            this.saveASnapshotIfNeeded()
            this.revisionNumber += 1
            this.snapshotId = Project.generateNewSnapshotId()
        }
    }

    trainingDataDidChange() {
        this.negativeSet.adjustSizeUsingScoutImages(this.positiveSet.images.length)
            .finally(() => {
                this.setNeedsSave()
            })
    }

    ////////////
    // Saving //
    ////////////

    private saveTimerID: number|null = null
    private saveIsNeeded = false
    saveError: Error|null = null
    private saveQueue: {projectId: string, snapshotId: string, content: any, retryCount?: number}[] = []
    isSaving = false

    setNeedsSave() {
        console.log("saving project")

        this.saveIsNeeded = true

        // schedule a save soon
        // don't immediately save since there might be a few operations
        // happening at once (e.g. dragging a few images onto the page)
        if (this.saveTimerID) {
            clearTimeout(this.saveTimerID)
            this.saveTimerID = null
        }

        this.saveTimerID = setTimeout(() => {
            this.saveTimerID = null
            this.saveASnapshotIfNeeded()
        }, 100)
    }

    saveASnapshotIfNeeded() {
        if (!this.saveIsNeeded) return

        const snapshotId = this.snapshotId
        const snapshotContent = this.toJSON()

        // update the local snapshots list
        if (this.snapshots !== null) {
            const snapshot = new ProjectSnapshot(snapshotContent)
            const previousIndex = this.snapshots.findIndex(s => s.snapshotId == snapshotId)

            if (previousIndex === -1) {
                this.snapshots.unshift(snapshot)
            } else {
                this.snapshots.splice(previousIndex, 1, snapshot)
            }
        }

        // post the update to the firebase save queue
        // remove anything in the saveQueue that this update overwrites
        _.remove(this.saveQueue, el => el.snapshotId === snapshotId)
        const saveQueueItem = {projectId: this.projectId, snapshotId, content: snapshotContent}
        this.saveQueue.push(saveQueueItem)
        console.debug('queued update for save...', saveQueueItem)

        // start the save loop (if it's not already running)
        this.saveLoop()
    }

    /**
     * Start the save loop, if it's not already running.
     *
     * Saves the entries in the saveQueue in sequence, until the list is empty.
     * If a save fails, retrys 3 times before abandoning that save queue item.
     */
    async saveLoop() {
        if (this.isSaving) return

        this.isSaving = true

        while (this.saveQueue.length > 0) {
            const saveQueueItem = this.saveQueue.shift()!
            console.debug('saving...', saveQueueItem)

            try {
                // try to save
                await projectStorage.setProjectSnapshot(
                    saveQueueItem.projectId, saveQueueItem.snapshotId, saveQueueItem.content
                )
                this.saveError = null
            } catch (error) {
                this.saveError = error as Error
                const retryCount = saveQueueItem.retryCount ?? 0

                if (retryCount < 3) {
                    saveQueueItem.retryCount = retryCount + 1
                    this.saveQueue.unshift(saveQueueItem)
                    console.warn('snapshot save failed. retrying...', error)
                } else {
                    console.error('failed to save snapshot', saveQueueItem, error)
                }

                // give a delay before trying again
                await delay(1000)
            }
        }

        this.isSaving = false
    }

    ///////////////////////
    // Snapshots history //
    ///////////////////////

    snapshots: ProjectSnapshot[] = []

    loadFromSnapshotJSON(json: any) {
        console.assert(json.projectId == this.projectId)

        this.snapshotId = json.snapshotId
        this._modelLayer = json.modelLayer ?? 'googlenet_5b'
        this.positiveSet = TrainingImageSet.fromJSON(json.positiveSet, this)
        this.negativeSet = NegativeTrainingImageSet.fromJSON(json.negativeSet, this)
        this.neuralLens = (json.neuralLens
                           ? NeuralLens.fromJSON(json.neuralLens)
                           : null)
        this._searchSet = (json.searchSet
                           ? SearchSet.subclassFromJSON(json.searchSet)
                           : defaultSearchSet)

        this.revisionNumber = json.revisionNumber ?? 0
        this._name = json.name ?? null
        this.creatorName = json.creatorName

        // older snapshots don't have publish info, so we need the 'if'
        this.publishInfo = (json.publishInfo
                            ? PublishInfo.fromJSON(json.publishInfo)
                            : new PublishInfo())

        return this
    }

    toJSON(): any {
        return {
            projectId: this.projectId,
            snapshotId: this.snapshotId,
            positiveSet: this.positiveSet.toJSON(),
            negativeSet: this.negativeSet.toJSON(),
            searchSet: this.searchSet.toJSON(),
            modelLayer: this.modelLayer,
            neuralLens: this.neuralLens?.toJSON() ?? null,
            revisionNumber: this.revisionNumber,
            name: this.name,
            creatorName: this.creatorName,
            date: Date.now(),
            publishInfo: this.publishInfo.toJSON(),
        }
    }

    static generateNewProjectId() {
        // ID prefixed with today's date for some human-readability
        // makeRandomId(6) provides 35 bits of entropy.
        const date = new Date()
        const shortYear = date.getUTCFullYear() - 2000

        return (shortYear.toString()
                + date.getUTCMonth().toLocaleString(undefined,
                                                    {minimumIntegerDigits: 2})
                + date.getUTCDay().toLocaleString(undefined,
                                                  {minimumIntegerDigits: 2})
                + makeRandomId(6))
    }

    static generateNewSnapshotId() {
        // ID prefixed with datetime
        // makeRandomId(6) provides 35 bits of entropy.
        const date = new Date()
        const shortYear = date.getUTCFullYear() - 2000

        return (shortYear.toString()
                + date.getUTCMonth().toLocaleString(undefined,
                                                    {minimumIntegerDigits: 2})
                + date.getUTCDay().toLocaleString(undefined,
                                                  {minimumIntegerDigits: 2})
                + date.getUTCHours().toLocaleString(undefined,
                                                    {minimumIntegerDigits: 2})
                + date.getUTCMinutes().toLocaleString(undefined,
                                                      {minimumIntegerDigits: 2})
                + date.getUTCSeconds().toLocaleString(undefined,
                                                      {minimumIntegerDigits: 2})
                + makeRandomId(6))
    }
}
