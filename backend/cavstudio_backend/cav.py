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

import uuid
from pathlib import Path
from typing import List

import msgpack
import numpy as np
from django.conf import settings
from sklearn import linear_model

from . import activations_cache
from .image_reference import ImageReference

CAV_FOLDER = Path(settings.MEDIA_ROOT) / 'cavs'


class CAV:
    @classmethod
    def learn_from(cls, positive_image_refs, negative_image_refs, model_layer):
        positive_activations, negative_activations = load_image_sets_normalized_activations(
            [positive_image_refs, negative_image_refs],
            model_layer=model_layer
        )

        x = np.concatenate([
            positive_activations,
            negative_activations,
        ])
        labels = np.concatenate([
            np.repeat(0, len(positive_activations)),
            np.repeat(1, len(negative_activations)),
        ])
        weights = np.concatenate([
            [i.weight for i in positive_image_refs],
            [i.weight for i in negative_image_refs],
        ])

        lm = linear_model.SGDClassifier(alpha=0.01, max_iter=1000, tol=1e-3, verbose=True)

        lm.fit(x, labels, sample_weight=weights)

        cav_vector = -1 * lm.coef_[0]
        cav_vector /= np.linalg.norm(cav_vector)

        return cls(id=uuid.uuid4(), vector=cav_vector, model_layer=model_layer)

    def __init__(self, id, vector, model_layer, stats=None):
        self.vector = vector
        self.model_layer = model_layer
        self.id = id
        self.stats = stats

    def to_dict(self):
        return {
            'vector': self.vector.tolist(),
            'id': str(self.id),
            'model_layer': self.model_layer,
            'stats': self.stats.to_dict() if self.stats else None
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(
            id=uuid.UUID(dict['id']),
            vector=np.array(dict['vector']),
            model_layer=dict['model_layer'],
            stats=CAVStats.from_dict(dict['stats']) if dict.get('stats') else None
        )

    @classmethod
    def load(cls, id):
        file_path = CAV_FOLDER / f'{id}.cav'
        with open(file_path, 'rb') as f:
            return cls.from_dict(msgpack.load(f))

    def save(self):
        CAV_FOLDER.mkdir(parents=True, exist_ok=True)
        file_path = CAV_FOLDER / f'{self.id}.cav'
        with open(file_path, 'wb') as f:
            msgpack.dump(self.to_dict(), f, use_single_float=True)

    def summary_string(self, max_length=20):
        digits = []
        digitset = '0123456789abcdefghijklmnopqrstuvwxyz'

        for i, x in enumerate(self.vector):
            if i >= max_length:
                break

            digitset_index = int(abs(x) * 500)
            digitset_index = max(0, min(len(digitset)-1, digitset_index))

            digits.append(digitset[digitset_index])

        return ''.join(digits)

    def update_stats_from_scores(self, scores: np.ndarray):
        self.stats = CAVStats.from_scores(scores)


class CAVStats:
    @classmethod
    def from_scores(cls, scores: np.ndarray):
        top_5_idx = (-scores).argsort()[:5]
        return cls(
            mean=np.mean(scores),
            stddev=np.std(scores),
            max=np.max(scores),
            min=np.min(scores),
            top_5_mean=np.mean(scores[top_5_idx]),
        )

    def __init__(self, mean, stddev, max, min, top_5_mean):
        self.mean = mean
        self.stddev = stddev
        self.max = max
        self.min = min
        self.top_5_mean = top_5_mean

    @classmethod
    def from_dict(cls, dict):
        return cls(
            mean=dict['mean'],
            stddev=dict['stddev'],
            max=dict['max'],
            min=dict['min'],
            top_5_mean=dict['top_5_mean'],
        )

    def to_dict(self):
        return {
            'mean': float(self.mean),
            'stddev': float(self.stddev),
            'max': float(self.max),
            'min': float(self.min),
            'top_5_mean': float(self.top_5_mean),
        }


def load_image_sets_normalized_activations(image_sets: List[ImageReference], model_layer):
    image_refs = []
    for image_set in image_sets:
        image_refs.extend(image_set)

    activations = activations_cache.get_normalized_activations(image_refs, model_layer=model_layer)

    start_i = 0
    activations_sets = []
    for image_set in image_sets:
        count = len(image_set)
        activations_sets.append(activations[start_i:start_i+count])
        start_i += count

    return activations_sets
