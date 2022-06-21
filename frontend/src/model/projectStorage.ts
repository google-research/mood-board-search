import Project from './Project'
import _ from 'lodash'
import ProjectSnapshot from './ProjectSnapshot'
import {CustomSearchSet} from './SearchSet'

class ProjectStorage {
    constructor() {
    }

    async ready() {
        // check that the backend server is up and running
        return
    }

    async getUserProjectsSummary(): Promise<any[]> {
        const response = await this.request({
            path: 'get_user_projects_summary',
        })
        return response.results
    }

    async getProjectWithSnapshotId(snapshotId: string): Promise<Project> {
        const snapshotsResponse = await this.request({
            path: 'get_all_snapshots_for_project_including_snapshot',
            data: {snapshotId}
        })

        let snapshots = snapshotsResponse.results.map((d: any) => new ProjectSnapshot(d.data))

        const project = new Project({
            snapshotId,
            snapshots: snapshots,
            publishedSnapshotId: null,
        })
        return project

    }

    async getProjectSnapshot(snapshotId: string): Promise<Object> {
        const response = await this.request({
            path: 'get_snapshot',
            data: {snapshotId},
        })

        return response.result.data
    }

    async setProjectSnapshot(projectId: string, snapshotId: string, projectSnapshotJSON: any) {
        await this.request({
            path: 'set_snapshot',
            data: {snapshotId, snapshot: projectSnapshotJSON},
            method: 'POST',
        })
    }

    async deleteSnapshotWithId(id: string) {
        await this.request({
            path: 'delete_snapshot',
            data: {snapshotId: id},
            method: 'POST',
        })
    }

    async publishSnapshot(projectId: string, snapshotId: string|null) {
        throw new Error('not yet implemented')
    }

    async getPublishedSnapshotId(projectId: string): Promise<string|null> {
        throw new Error('not yet implemented')
    }

    async getSearchSets(): Promise<CustomSearchSet[]> {
        const response = await this.request({
            path: 'get_search_sets',
        })

        return response.results.filter((d: any) => (
            !d.data.deleted
        )).map((d: any) => (
            CustomSearchSet.fromJSON(d.data)
        ))
    }

    async getSearchSetWithId(id: string): Promise<CustomSearchSet> {
        const response = await this.request({
            path: 'get_search_set',
            data: {searchSetId: id},
        })

        return CustomSearchSet.fromJSON(response.result.data)
    }

    async setSearchSet(id: string, searchSetJson: any) {
        await this.request({
            path: 'set_search_set',
            data: {searchSetId: id, searchSet: searchSetJson},
            method: 'POST',
        })
    }

    async deleteSearchSetWithId(id: string) {
        await this.request({
            path: 'delete_search_set',
            data: {searchSetId: id},
            method: 'POST',
        })
    }

    async copySnapshotToNewProject(options: {
        srcSnapshotId: string,
        dstProjectId: string,
        dstSnapshotId: string,
        dstName: string,
    }) {
        const {srcSnapshotId, dstProjectId, dstSnapshotId, dstName} = options
        await this.request({
            path: 'copy_snapshot_to_new_project',
            data: {srcSnapshotId, dstProjectId, dstSnapshotId, dstName},
            method: 'POST',
        })
    }

    private async request(options: {path: string, data?: any, method?: string}): Promise<any> {
        let {path, data=null, method='GET'} = options;

        let url = `http://localhost:8000/api/db/`+path

        const fetchOptions: RequestInit = {
            method,
            headers: {
                accept: 'application/json',
            }
        }

        if (data) {
            if (method == 'GET') {
                url += '?' + (new URLSearchParams(data)).toString();
            } else {
                fetchOptions.body = JSON.stringify(data);
                // @ts-ignore
                fetchOptions.headers['Content-type'] = 'application/json'
            }
        }

        const response = await fetch(url, fetchOptions)

        if (!response.ok) {
            throw Error(`HTTP error ${response.status} ${response.statusText}`)
        }

        const contentType = response.headers.get('content-type')

        if (contentType && contentType.includes('application/json')) {
            return await response.json()
        }

        return null
    }
}

const projectStorage = new ProjectStorage();
export default projectStorage;
