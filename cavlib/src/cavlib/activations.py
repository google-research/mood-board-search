# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import typing
from pathlib import Path
from typing import IO, Any, Dict, Union

import numpy as np
import PIL.Image
import skimage.transform
from typing_extensions import Literal

from cavlib.models import GooglenetModel, MobilenetModel, Model
from cavlib.typing import ArrayLike, NDArray

ModelLayer = Literal['mobilenet_12d', 'googlenet_4d', 'googlenet_5b']
MODEL_LAYER_MOBILENET_12D: ModelLayer = 'mobilenet_12d'
MODEL_LAYER_GOOGLENET_4D: ModelLayer = 'googlenet_4d'
MODEL_LAYER_GOOGLENET_5B: ModelLayer = 'googlenet_5b'
MODEL_LAYERS = [MODEL_LAYER_MOBILENET_12D, MODEL_LAYER_GOOGLENET_4D, MODEL_LAYER_GOOGLENET_5B]

CAVableImage = Union[str, Path, IO[bytes], PIL.Image.Image, ArrayLike]
ModelClassName = Literal['GooglenetModel', 'MobilenetModel']
loaded_models: Dict[str, Model] = {}


def compute_activations(
    image: CAVableImage, *, model_layer: ModelLayer = MODEL_LAYER_GOOGLENET_4D
) -> NDArray[np.float32]:
    '''compute_activations(image, model_layer='googlenet_4d')
    Calculates activations for a given image. Activations are the value of
    each neuron in the network at that layer.

    This function can be used to precalculate activations for a set of images,
    so they don't have to be calculated every time. Activations can be used
    with :func:`cavlib.CAV.score` and :class:`cavlib.train.TrainingImage`.

    :param CAVableImage image: The image whose activations we want to calculate. Accepts
        a path to an image file, an open file-like object of an image, a PIL
        Image, or a numpy array of RGB data
    :param str model_layer: The :ref:`model layer <model-layers>` to extract.

    :returns: The activation vector, as a 1D numpy array.
    '''
    pixels = get_pixels(image)

    model_layer_info = get_model_layer_info(model_layer)
    model = get_model_instance(model_layer_info.model_class_name)

    return model.get_activation_for_image(pixels, model_layer_info.layer_name)


def get_pixels(image: CAVableImage) -> NDArray[Any]:
    if isinstance(image, str) or hasattr(image, '__fspath__') or hasattr(image, 'read'):
        pil_image = PIL.Image.open(image)  # type: ignore
        array = np.array(pil_image)
    else:
        array = np.array(image)

    return crop_to_square_and_resize(array, width=224)


def get_model_instance(model_class_name: ModelClassName) -> Model:
    if model_class_name not in loaded_models:
        if model_class_name == 'GooglenetModel':
            model: Model = GooglenetModel()
        elif model_class_name == 'MobilenetModel':
            model = MobilenetModel()
        else:
            raise ValueError('unknown model class')

        loaded_models[model_class_name] = model

    return loaded_models[model_class_name]


class ModelLayerInfo(typing.NamedTuple):
    model_class_name: ModelClassName
    layer_name: str


def get_model_layer_info(model_layer: ModelLayer) -> ModelLayerInfo:
    if model_layer == 'googlenet_4d':
        return ModelLayerInfo('GooglenetModel', 'mixed4d')
    elif model_layer == 'googlenet_5b':
        return ModelLayerInfo('GooglenetModel', 'mixed5b')
    elif model_layer == 'mobilenet_12d':
        return ModelLayerInfo('MobilenetModel', 'MobilenetV1/MobilenetV1/Conv2d_12_depthwise/Relu6')
    else:
        raise ValueError(f'unknown model_layer: {model_layer}')


def crop_to_square_and_resize(image: NDArray[Any], width: int) -> NDArray[Any]:
    if image.shape[0] == width and image.shape[1] == width:
        return image

    scale_factor = max(width / image.shape[0], width / image.shape[1])

    translate_x = image.shape[1] / 2 * scale_factor - width / 2
    translate_y = image.shape[0] / 2 * scale_factor - width / 2

    # crop and resize in one operation for efficiency
    return skimage.transform.warp(
        image,
        skimage.transform.SimilarityTransform(
            scale=1/scale_factor, translation=(translate_x/scale_factor, translate_y/scale_factor)
        ),
        output_shape=(width, width),
        mode='edge',
    )
