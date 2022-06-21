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
