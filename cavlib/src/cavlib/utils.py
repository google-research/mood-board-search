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
from typing import Any, Tuple
import numpy as np
from cavlib.typing import NDArray


class ArrayShapeError(TypeError):
    pass


def assert_shape(x: NDArray[Any], shape: Tuple[int, ...]) -> None:
    """ e.g.: assert_shape(conv_input_array, [8, 3, None, None]) """
    if not shape_equal(x, shape):
        x_shape = np.shape(x)
        raise ArrayShapeError(f'Argument has the incorrect shape. Expected {shape}, received {x_shape}.')


def shape_equal(x: NDArray[Any], shape: Tuple[int, ...]) -> bool:
    """ e.g.: shape_equal(conv_input_array, [8, 3, None, None]) """
    x_shape = np.shape(x)
    if len(x_shape) != len(shape):
        return False

    for _a, _b in zip(x_shape, shape):
        if isinstance(_b, int):
            if _a != _b:
                return False
    return True


def cosine_similarity(vector1: NDArray[Any], vector2: NDArray[Any]) -> float:
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
