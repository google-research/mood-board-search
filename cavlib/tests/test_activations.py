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

from cavlib import compute_activations
from tests.utils import TEST_IMAGE, TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D, TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B, TEST_IMAGE_ACTIVATIONS_MOBILENET_12D, cosine_similarity
import numpy as np
import pytest
import PIL.Image

@pytest.mark.parametrize('model_layer', ['googlenet_4d', 'googlenet_5b', 'mobilenet_12d'])
def test_get_activations_inputs(model_layer):
    if model_layer == 'googlenet_4d':
        expected_activations = np.load(TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D)
    elif model_layer == 'googlenet_5b':
        expected_activations = np.load(TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B)
    elif model_layer == 'mobilenet_12d':
        expected_activations = np.load(TEST_IMAGE_ACTIVATIONS_MOBILENET_12D)
    else:
        assert False

    with open(TEST_IMAGE, 'rb') as file_object:
        image_formats = [
            str(TEST_IMAGE),  # a str
            TEST_IMAGE,  # pathlib.Path
            file_object,
            PIL.Image.open(TEST_IMAGE),  # a Pillow image
            np.array(PIL.Image.open(TEST_IMAGE)),  # a numpy array
        ]

        for image_format in image_formats:
            acts = compute_activations(image_format, model_layer=model_layer)
            assert cosine_similarity(acts, expected_activations) == pytest.approx(1.0, rel=0.001)
