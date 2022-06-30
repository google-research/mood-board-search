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

import cavServer, { CropSpec, CropsResponse } from './cavServer'
import { CAVServerImage } from './CAVImage';
import _ from 'lodash'
import Semaphore from '../../../third_party/Semaphore';
;

export interface Ticket<T> {
    cacheKey: string;
    isLoading: boolean;
    wasCancelled: boolean;
    result: T|null;
    error: Error|null;
}

interface PromiseTicket<T> extends Ticket<T> {
    load: () => Promise<T>;
    promise: Promise<T>|null;
}

class ImageInspectCache {
    // TODO (joerick): combine heatmap/focus inspect cache with top crop
    cropCache: {[k: string]: CropsResponse} = {}
    queue: PromiseTicket<CropsResponse>[] = []

    queueRunning = false;
    queueSemaphore = new Semaphore(1)

    getTopCrops(image: CAVServerImage, cavId: string): Ticket<CropsResponse> {
        // check in the cache
        const cacheKey = `crops-${image.id}-${cavId}`;

        if (this.cropCache[cacheKey]) {
            // was already cached
            return {
                cacheKey,
                isLoading: false,
                wasCancelled: false,
                result: this.cropCache[cacheKey],
                error: null
            }
        }

        let ticket = _.find(this.queue, el => el.cacheKey == cacheKey)

        if (ticket) {
            // task already queued, return existing ticket
            return ticket;
        }

        ticket = {
            cacheKey,
            isLoading: false,
            wasCancelled: false,
            result: null,
            error: null,
            promise: null,
            load: async () => {
                const response = await cavServer.getImageCrops({image, cavId})
                this.cropCache[cacheKey] = response
                return response
            }
        }
        this.addToQueue(ticket)
        return ticket
    }

    addToQueue(ticket: PromiseTicket<any>) {
        this.queue.push(ticket);

        this.queueSemaphore.use(async () => {
            if (ticket.wasCancelled) return;

            const queueTicketIndex = this.queue.indexOf(ticket);

            if (queueTicketIndex == -1) {
                throw new Error("ticket wasn't cancelled but isn't in the queue anymore");
            }
            // remove that ticket from the queue
            this.queue.splice(queueTicketIndex, 1)

            ticket.isLoading = true;
            ticket.promise = ticket.load()

            try {
                ticket.result = await ticket.promise
            }
            catch (error) {
                ticket.error = error;
            }
            finally {
                ticket.isLoading = false;
            }
        })
    }

    clearQueue() {
        this.queue.forEach(ticket => { ticket.wasCancelled = true })
        // remove everything from the queue
        this.queue.splice(0, this.queue.length)
    }
}

const imageInspectCache = new ImageInspectCache();
(window as any).imageInspectCache = imageInspectCache;
export default imageInspectCache;
