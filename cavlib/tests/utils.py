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
import numpy as np

TEST_DATA_DIR = Path(__file__).parent / 'test_data'
TEST_IMAGE = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.224x224.png'
TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_4d.npy'
TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_5b.npy'
TEST_IMAGE_ACTIVATIONS_MOBILENET_12D = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.mobilenet_12d.npy'


def cosine_similarity(arr1, arr2):
    return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
