import { CAVServerImage } from './CAVImage';
import _ from 'lodash';
import projectStorage from './projectStorage';
import {makeRandomId} from '@/util'

export abstract class SearchSet {
    abstract readonly name: string
    abstract readonly creatorName: string
    abstract readonly images: CAVServerImage[]|null;
    abstract readonly vueKey: string
    abstract readonly isCustom: boolean

    static subclassFromJSON(json: any) {
        if (json == 'default') {
            return defaultSearchSet;
        } else {
            return CustomSearchSet.fromJSON(json)
        }
    }
    abstract toJSON(): any
}

export class BuiltInSearchSet extends SearchSet {
    readonly name: string
    readonly creatorName: string
    get images() { return null }
    get vueKey() { return 'default' }
    get isCustom() { return false }

    constructor(options: {name: string, creatorName: string}) {
        super()
        this.name = options.name
        this.creatorName = options.creatorName
    }

    toJSON() {
        return 'default'
    }
}

export const defaultSearchSet = new BuiltInSearchSet({
    name: 'Sample set',
    creatorName: 'Nord Projects',
})

export class CustomSearchSet extends SearchSet {
    searchSetId: string
    _name: string = 'untitled-search-set'
    images: CAVServerImage[] = []
    creatorName: string = ''
    owner: string|null = null // owner is null until the first save
    parentId: string|null = null

    get vueKey() { return this.searchSetId }
    get isCustom() { return true }

    get name() { return this._name }
    set name(value) {
        if (value === this._name) return;

        this._name = value
        this.save()
    }

    constructor() {
        super()
        this.searchSetId = makeRandomId(9)
        this.creatorName = 'you'
    }

    static fromJSON(json: any) {
        const searchSet = new this()
        searchSet.searchSetId = json.searchSetId
        searchSet._name = json.name
        searchSet.images = json.images.map((imageJSONs: any) => (
            CAVServerImage.fromJSON(imageJSONs)
        ))
        searchSet.creatorName = json.creatorName
        searchSet.owner = json.owner
        searchSet.parentId = json.parentId ?? null
        return searchSet
    }

    toJSON() {
        return {
            searchSetId: this.searchSetId,
            images: this.images.map(i => i.toJSON()),
            imageCount: this.images.length,
            name: this.name,
            creatorName: this.creatorName,
            parentId: this.parentId,
        }
    }

    async save() {
        if (this.images.length === 0) {
            throw new Error("Can't save search set because it has no images")
        }
        await projectStorage.setSearchSet(this.searchSetId, this.toJSON())
    }

    createCopy(): CustomSearchSet {
        var newSet = new CustomSearchSet()
        newSet = Object.assign(newSet, this)
        newSet.searchSetId = makeRandomId(9)
        newSet.parentId = this.searchSetId
        newSet.owner = null

        return newSet
    }
}
