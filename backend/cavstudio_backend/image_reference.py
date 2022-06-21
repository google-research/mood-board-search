import hashlib
import io
import multiprocessing.pool
from pathlib import Path
from typing import List

import numpy as np
import PIL
import PIL.Image
from django.conf import settings
from tqdm import tqdm

from .ml_engine import MODEL_LAYERS, ml_engine
from .utils import assert_shape, split_into_chunks


def image_hash(pil_image):
    assert pil_image.mode == 'RGB'

    pixels = np.array(pil_image, dtype='<u1')
    pixel_buffer = pixels.tobytes(order='C')

    return hashlib.md5(pixel_buffer).hexdigest()


def injest_image(image_data_224, image_data_1200, user_generated=False):
    image224 = PIL.Image.open(io.BytesIO(image_data_224))

    if image224.mode != 'RGB':
        image224 = image224.convert('RGB')

    id = image_hash(image224)

    image = ImageReference(id=id, user_generated=user_generated)

    content_dir = cav_content_dir(user_generated=user_generated)

    if not content_dir.exists():
        content_dir.mkdir(parents=True)

    if not image.image_224_path.exists():
        image224.save(str(image.image_224_path))

    if not image.image_1200_path.exists():
        image.image_1200_path.write_bytes(image_data_1200)

    activations_needed = [ml for ml in MODEL_LAYERS if not image.activations_path(ml).exists()]
    if len(activations_needed) > 0:
        pixels = np.array(image224)
        assert_shape(pixels, (224, 224, 3))
        activations = ml_engine.calculate_activations(activations_needed, [pixels])[0]

        for model_layer, activation_array in activations.items():
            np.save(image.activations_path(model_layer), activation_array)

    return image


class ImageReference:
    def __init__(self, *, id, user_generated=False):
        # don't want subdir shenanegans
        assert '/' not in id
        self.id = id
        self.user_generated = user_generated

    @property
    def image_224_path(self):
        filename = '{}.1x.224x224.png'.format(self.id)
        return cav_content_dir(self.user_generated) / filename

    @property
    def image_1200_path(self):
        filename = '{}.1x.1200x1200.jpg'.format(self.id)
        return cav_content_dir(self.user_generated) / filename

    def activations_path(self, model_layer):
        filename = '{}.1x.{}.npy'.format(self.id, model_layer)
        return cav_content_dir(self.user_generated) / filename

    @classmethod
    def from_json(cls, json: dict):
        return cls(id=json['id'], user_generated=json['user_generated'])

    def to_json(self):
        return {
            'id': self.id,
            'user_generated': self.user_generated,
        }


class TrainingImageReference(ImageReference):
    def __init__(self, *, id, user_generated=False):
        super().__init__(id=id, user_generated=user_generated)
        self.weight = 1

    @classmethod
    def from_json(cls, json: dict):
        result = super().from_json(json=json)
        result.weight = json.get('weight', 1)
        return result

    def to_json(self):
        result = super().to_json()
        result['weight'] = self.weight
        return result


activations_load_pool = multiprocessing.pool.ThreadPool(12)


def load_activations(image_refs: List[ImageReference], model_layer: str, normalize=False):
    activations_paths = [i.activations_path(model_layer) for i in image_refs]

    if normalize:
        load_fn = load_and_normalize_activation
    else:
        load_fn = np.load

    return activations_load_pool.map(load_fn, activations_paths)


def load_and_normalize_activation(activation_path):
    activation = np.load(activation_path)
    activation /= np.linalg.norm(activation)
    return activation


def cav_content_dir(user_generated):
    if user_generated:
        content_dir = Path(settings.MEDIA_ROOT) / 'cav-content'
    else:
        content_dir = Path(settings.STATIC_CAV_CONTENT_ROOT)

    return content_dir


def image_refs_that_need_activations(image_refs: List[ImageReference]):
    '''
    Returns the image refs that are missing activations
    '''
    # remove duplicate images from image_refs
    image_refs = list({i.id: i for i in image_refs}.values())

    result = []

    for image_ref in image_refs:
        needs_activations = any(not image_ref.activations_path(ml).exists() for ml in MODEL_LAYERS)
        if needs_activations:
            result.append(image_ref)

    return result


def precalculate_activations(image_refs: List[ImageReference]):
    '''
    Calculate and store activations for each image ref
    '''
    image_refs = image_refs_that_need_activations(image_refs=image_refs)

    # calculate and save activations
    for image_ref in tqdm(image_refs, unit='image'):
        image = PIL.Image.open(image_ref.image_224_path)
        image_pixels = np.array(image)

        activations_dict = ml_engine.calculate_activations(MODEL_LAYERS, [image_pixels])[0]

        for model_layer in MODEL_LAYERS:
            activations_path = image_ref.activations_path(model_layer)
            np.save(activations_path, activations_dict[model_layer])
