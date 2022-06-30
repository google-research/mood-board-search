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
from typing import Any, Dict, List, Optional, Sequence, TypeVar
import uuid
from pathlib import Path

import msgpack
import numpy as np

from cavlib.activations import CAVableImage, ModelLayer, compute_activations
from cavlib.utils import cosine_similarity
from cavlib.typing import NDArray


T_CAVableImage = TypeVar('T_CAVableImage', bound=CAVableImage)

class CAV:
    def __init__(
        self,
        id: uuid.UUID,
        vector: NDArray[np.float32],
        model_layer: ModelLayer,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        '''
        This class represents a CAV object. CAVs are normally created by
        loading them from disk with :func:`CAV.load` or by training them
        :func:`train_cav`.
        '''
        self.id = id
        self.vector = vector
        self.model_layer: ModelLayer = model_layer
        self.metadata = metadata or {}
        # unrecognised elements in the msgpack are passed through via the
        # 'extra' dict
        self._extra: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'vector': self.vector.tolist(),
            'id': str(self.id),
            'model_layer': self.model_layer,
            'metadata': self.metadata,
            **self._extra,
        }

    @classmethod
    def from_dict(cls, a_dict: Dict[str, Any]) -> CAV:
        a_dict = a_dict.copy()

        result = cls(
            id=uuid.UUID(a_dict.pop('id')),
            vector=np.array(a_dict.pop('vector')),
            model_layer=a_dict.pop('model_layer'),
            metadata=a_dict.pop('metadata', None),
        )

        result._extra = a_dict # the remaining elements are stored as `_extra`

        return result

    @classmethod
    def load(cls, path: str | Path) -> CAV:
        '''
        Load a CAV from file.

        :param path: The path to the CAV file to load.
        :return: the CAV object.
        '''
        with open(path, 'rb') as f:
            file_contents = msgpack.load(f)

            if not isinstance(file_contents, dict):
                raise TypeError(f'Failed to load CAV from file at {path}. Expected `dict`, got {type(file_contents)}.')

            return cls.from_dict(file_contents)

    def save(self, path: str | Path) -> None:
        '''
        Save the CAV file to disk.

        :param path: The path to save to. The file is created if it does not
            exist, otherwise the existing file is overwritten. We recommend
            using a file extension of ``.cav``.
        '''
        with open(path, 'wb') as f:
            msgpack.dump(self.to_dict(), f, use_single_float=True)

    def score(self, image_or_activation: CAVableImage | NDArray[np.float32]) -> float:
        '''
        Calculates the CAV score for an image.

        :param image_or_activation: The image to score according to this CAV.
            Can be any of the :ref:`supported image formats <CAVableImage>`,
            or a precomputed activation (e.g. from :func:`get_activations`)
        '''
        if isinstance(image_or_activation, np.ndarray) and len(image_or_activation.shape) == 1:
            # a 1D vector input means this is an activation.
            image_activations = image_or_activation
        else:
            image_activations = compute_activations(
                image_or_activation,
                model_layer=self.model_layer
            )

        return cosine_similarity(self.vector, image_activations)

    def sort(self, images: Sequence[T_CAVableImage], reverse: bool = False) -> List[T_CAVableImage]:
        return sorted(images, key=lambda im: self.score(im), reverse=reverse)
