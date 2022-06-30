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

import EXIF from 'exif-js'

export function loadImage(url: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
        const image = new Image()

        image.onload = () => {
            resolve(image);
        }
        image.onerror = (error) => {
            reject(error);
        }

        image.src = url
    })
}

export async function getEXIFOrientation(image: HTMLImageElement): Promise<number> {
    return new Promise(res => {
        EXIF.getData(<any>image, function (this: any) {
            const img = this;

            console.log('exif!', img.exifdata)
            res(img.exifdata?.Orientation ?? 1)
        })
    })
}

/**
 * Returns a canvas of size `options.size`, containing `image`, drawn to fill
 * the canvas.
 */
export function drawImageToCanvas(options: {image: HTMLImageElement, exifOrientation: number, size: {width: number, height: number}}) {
    const {image, exifOrientation, size} = options;
    const xScaleFactor = image.width / size.width;
    const yScaleFactor = image.height / size.height;

    const scaleFactor = Math.min(xScaleFactor, yScaleFactor)

    const canvas = document.createElement('canvas');
    canvas.width = size.width;
    canvas.height = size.height;

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        throw new Error('failed to get a draw context')
    }

    switch(exifOrientation) {
        case 2:
            // horizontal flip
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            break;
        case 3:
            // 180° rotate left
            ctx.translate(canvas.width, canvas.height);
            ctx.rotate(Math.PI);
            break;
        case 4:
            // vertical flip
            ctx.translate(0, canvas.height);
            ctx.scale(1, -1);
            break;
        case 5:
            // vertical flip + 90 rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.scale(1, -1);
            break;
        case 6:
            // 90° rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.translate(0, -canvas.height);
            break;
        case 7:
            // horizontal flip + 90 rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.translate(canvas.width, -canvas.height);
            ctx.scale(-1, 1);
            break;
        case 8:
            // 90° rotate left
            ctx.rotate(-0.5 * Math.PI);
            ctx.translate(-canvas.width, 0);
            break;
    }

    ctx.imageSmoothingQuality = 'high'
    ctx.drawImage(image,
                  /*sx:*/ image.width/2 - size.width*scaleFactor/2,
                  /*sy:*/ image.height/2 - size.height*scaleFactor/2,
                  /*sw:*/ size.width*scaleFactor,
                  /*sh:*/ size.height*scaleFactor,
                  /*dx:*/ 0,
                  /*dy:*/ 0,
                  /*dw:*/ size.width,
                  /*dh:*/ size.height)
    return canvas
}
