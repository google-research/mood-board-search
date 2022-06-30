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

export function debugShowImage(url: string) {
    const image = document.createElement('img')
    image.src = url
    image.style.position = 'absolute'
    image.style.top = '0'
    image.style.left = '0'
    image.style.cursor = 'not-allowed'
    image.addEventListener('click', () => image.remove())
    document.body.append(image);
}

export function makeRandomId(length: number) {
    /**
     * Generate an ASCII alphanumeric ID.
     * Provides 5.95 bits of entropy per character.
     */
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

export function delay(millis: number): Promise<void> {
    return new Promise(resolve => {
        setTimeout(resolve, millis)
    })
}

import moment from 'moment';

export function snapshotDateFormat(date: Date) {
    var today = moment();
    var weekAgo = moment().subtract(6, 'days').startOf('day');

    var dateString;
    if (moment(date).isSame(today, 'day'))  {
        dateString = "Today"
    } else if (moment(date).isAfter(weekAgo)) {
        dateString = moment(date).format('ddd')
    } else {
        var formatL = moment.localeData().longDateFormat('L');
        var formatYearlessL = formatL.replace(/YYYY/g,'YY');
        var formatYearlessL = formatYearlessL.replace(/\//g, '.');
        dateString = moment(date).format(formatYearlessL);
    }

    var timeString = moment(date).format('h:mma');
    return timeString + ', ' + dateString
}

export function projectDateFormat(date: Date) {
    var today = moment();
    var yesterday = moment().subtract(1, 'day');
    const time = moment(date).format('h:mma');

    if (moment(date).isSame(today, 'day')) {
        return 'Today ' + time
    } else if (moment(date).isSame(yesterday, 'day')) {
        return 'Yesterday ' + time
    }
    return moment(date).fromNow();
}
