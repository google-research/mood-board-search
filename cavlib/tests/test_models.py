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

from pathlib import Path
from cavlib import models
import pytest
import PIL.Image
import numpy as np
import json
import skimage.util

from tests.utils import (
    TEST_IMAGE,
    TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D,
    TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B,
    TEST_IMAGE_ACTIVATIONS_MOBILENET_12D,
    cosine_similarity,
)


def test_layer_names():
    model = models.GooglenetModel()
    assert "mixed4d" in model.output_layer_names
    assert "mixed5b" in model.output_layer_names

    model = models.MobilenetModel()
    assert (
        "MobilenetV1/MobilenetV1/Conv2d_12_depthwise/Relu6" in model.output_layer_names
    )


def test_consistent_activations():
    model = models.GooglenetModel()

    input_image = np.array(PIL.Image.open(TEST_IMAGE))
    activations1 = model.get_activation_for_image(input_image, layer_name="mixed4d")
    activations2 = model.get_activation_for_image(input_image, layer_name="mixed4d")

    assert activations1 == pytest.approx(activations2)


@pytest.mark.parametrize("model_cls,layer_name,precomputed_activation", [
        (models.GooglenetModel, "mixed4d", TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D),
        (models.GooglenetModel, "mixed5b", TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B),
        (models.MobilenetModel, "MobilenetV1/MobilenetV1/Conv2d_12_depthwise/Relu6", TEST_IMAGE_ACTIVATIONS_MOBILENET_12D),
    ],
)
@pytest.mark.parametrize("array_type", ['original', 'skimage'])
def test_activations_match_tensorflow_versions(model_cls, layer_name, precomputed_activation, array_type):
    model = model_cls()

    input_image = np.array(PIL.Image.open(TEST_IMAGE))

    if array_type == 'skimage':
        input_image = skimage.util.img_as_float32(input_image)

    activation = model.get_activation_for_image(input_image, layer_name=layer_name)

    tensorflow_activation = np.load(precomputed_activation)

    cosine_sim = cosine_similarity(activation, tensorflow_activation)
    distance = np.linalg.norm(activation - tensorflow_activation)

    print('cosine similarity: ', cosine_sim)
    print('euclidian distance: ', distance)

    assert cosine_sim == pytest.approx(1.0, rel=0.001)
    assert distance == pytest.approx(0.0, abs=0.1)
