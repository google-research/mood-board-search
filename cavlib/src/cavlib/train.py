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

import uuid
from typing import Dict, List, Optional, Sequence, Union

import numpy as np
import sklearn.linear_model

from cavlib.activations import MODEL_LAYER_GOOGLENET_4D, CAVableImage, ModelLayer, compute_activations
from cavlib.cav import CAV
from cavlib.typing import NDArray


class TrainingImage:
    image: Optional[CAVableImage]
    activations: Dict[ModelLayer, NDArray[np.float32]]
    weight: float

    def __init__(
        self,
        image: Optional[CAVableImage] = None,
        activations: Optional[Dict[ModelLayer, NDArray[np.float32]]] = None,
        weight: float = 1.0,
    ) -> None:
        '''
        This object represents an image used for training a CAV. It's use in
        training is optional, but it has a few functions:

        - if you want to supply weights when training, you can do so using the ``weight`` attribute.
        - it caches activations in-memory
        - if you want to avoid computing model activations at all, you can create the TrainingImage with
          a precalculated ``activations`` dict.

        :param image: the image to be used for training. Can be ``None``, if ``activations`` is
            passed.
        :param activations: a dictionary of activations, keyed by model_layer. e.g.
            ``{"googlenet_4d": np.ndarray(<your activation>)}``. Used to supply precomputed
            activations, if you have them.
        :param weight: the weight of this image in training. Defaults to 1. To upweight an image,
            set it to a larger value, like 4.
        '''
        if image is None and activations is None:
            raise ValueError('you must supply either an image or a dict of activations to create a TrainingImage')

        self.image = image
        self.weight = weight
        self.activations = activations if activations is not None else {}

    def activations_for_model_layer(self, model_layer: ModelLayer) -> NDArray[np.float32]:
        if model_layer not in self.activations:
            if not self.image:
                raise ValueError(f'{model_layer} activations not found in `activations` dict')

            self.activations[model_layer] = compute_activations(self.image, model_layer=model_layer)

        return self.activations[model_layer]


def train_cav(
    *,
    positive_images: Sequence[CAVableImage | TrainingImage],
    negative_images: Sequence[CAVableImage | TrainingImage],
    model_layer: ModelLayer = MODEL_LAYER_GOOGLENET_4D,
    random_state: Optional[np.random.RandomState] = None
) -> CAV:
    '''
    Create a new CAV by training it on the given positive and negative samples.

    :param positive_images: A list of images that represent the concept.
    :param negative_images: A list of images that don't represent the concept.
        These can either be random images, or, even better, images that
        represent the opposite of the concept you're trying to capture.
    :param model_layer: The :ref:`model layer <model-layers>` that you want the new CAV to use.
    :param random_state: A supply of randomness. Training CAVs is
        nondeterministic, due to the SGDClassifier linear model that CAVlib
        uses. This is not normally a problem, but if you require consistent,
        deterministic results (for example, in regression tests), set this to
        a fresh instance of ``numpy.random.RandomState`` that has been seeded
        to a constant, and ensure that your training images are always in the
        same order.

    The image arguments can either be :ref:`images <CAVableImage>` (e.g. a
    path, a PIL.Image or numpy array of pixels), or :class:`TrainingImage`
    objects. TrainingImage objects provide more flexibility - they can include
    weights, or, if you have a precalculated activation, this can be used via
    a TrainingImage.
    '''
    positive_training_images = [
        im if isinstance(im, TrainingImage) else TrainingImage(im)
        for im in positive_images
    ]
    negative_training_images = [
        im if isinstance(im, TrainingImage) else TrainingImage(im)
        for im in negative_images
    ]

    positive_activations = [
        t.activations_for_model_layer(model_layer)
        for t in positive_training_images
    ]
    negative_activations = [
        t.activations_for_model_layer(model_layer)
        for t in negative_training_images
    ]

    x = np.concatenate([
        positive_activations,
        negative_activations,
    ])
    labels = np.concatenate([
        np.repeat(0, len(positive_activations)),
        np.repeat(1, len(negative_activations)),
    ])
    weights = np.concatenate([
        [i.weight for i in positive_training_images],
        [i.weight for i in negative_training_images],
    ])

    lm = sklearn.linear_model.SGDClassifier(
        alpha=0.01, max_iter=1000, tol=1e-3, random_state=random_state
    )

    lm.fit(x, labels, sample_weight=weights)

    cav_vector = -1 * lm.coef_[0]  # type: ignore
    cav_vector /= np.linalg.norm(cav_vector)
    return CAV(id=uuid.uuid4(), vector=cav_vector, model_layer=model_layer)
