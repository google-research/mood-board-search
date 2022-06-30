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

import multiprocessing
from functools import lru_cache
from typing import List

from .image_reference import ImageReference, load_and_normalize_activation

activations_get_pool = multiprocessing.pool.ThreadPool(12)


# Each activation is 100-400kB each, so 8000 caches would be somewhere between
# 0.8 - 3.2GB in RAM.
@lru_cache(typed=False, maxsize=8000)
def get_normalized_activation(activation_path):
    return load_and_normalize_activation(activation_path)


def get_normalized_activations(image_refs: List[ImageReference], model_layer: str):
    activation_paths = [i.activations_path(model_layer=model_layer) for i in image_refs]
    return activations_get_pool.map(get_normalized_activation, activation_paths)
