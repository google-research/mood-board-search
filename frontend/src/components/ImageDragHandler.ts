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

import TrainingImageSet from '@/model/TrainingImageSet';

export default class ImageDragHandler {
  imagesAboutToDrop = 0
  allowedImageTypes = ['image/jpeg', 'image/gif', 'image/png'];

  constructor(
    readonly element: Element,
    readonly imageFilesCallback: (imageFiles: File[]) => void,
  ) {}

  shouldAccept(item: File|DataTransferItem) {
    return this.allowedImageTypes.includes(item.type)
  }

  dragenter(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
  }
  dragover(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();

    if (!event.dataTransfer) return;
    let imageCount = 0;

    for (const item of Array.from(event.dataTransfer.items ?? [])) {
      if (item.kind == 'file' && this.shouldAccept(item)) {
        imageCount += 1;;
      }
    }

    if (imageCount > 0) {
      event.dataTransfer.dropEffect = 'copy';
    } else {
      event.dataTransfer.dropEffect = 'none';
    }

    this.imagesAboutToDrop = imageCount;
  }
  dragleave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();

    const related = event.relatedTarget as HTMLElement;
    if (this.element === related) return;
    if (this.element.contains(related)) return;

    this.imagesAboutToDrop = 0;
  }
  drop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    if (!event.dataTransfer) return;

    const files = Array.from(event.dataTransfer.files)
    const imageFiles = files.filter(f => this.shouldAccept(f))

    this.imageFilesCallback(imageFiles)
    this.imagesAboutToDrop = 0;
  }
}
