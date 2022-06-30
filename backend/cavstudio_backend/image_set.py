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

import json
from functools import lru_cache
from pathlib import Path

from cached_property import threaded_cached_property as cached_property
from django.conf import settings

from . import activations_cache
from .image_reference import ImageReference, load_activations
from .ml_engine import MODEL_LAYERS


class BuiltInImageSet:
    def __init__(self, version_name):
        assert '/' not in version_name
        manifest_file = Path(settings.STATIC_CAV_CONTENT_ROOT) / 'manifests' / f'{version_name}.json'
        if not manifest_file.exists():
            raise BuiltInImageSet.VersionNotFound()

        with open(manifest_file) as f:
            manifest_contents = json.load(f)

        self.image_refs = [ImageReference(id=image_dict['id'], user_generated=False)
                           for image_dict in manifest_contents['images']]

    @cached_property
    def all_normalized_activations(self):
        results = {}

        for model_layer in MODEL_LAYERS:
            results[model_layer] = load_activations(
                self.image_refs,
                model_layer=model_layer,
                normalize=True
            )

        return results

    def normalized_activations(self, model_layer):
        return self.all_normalized_activations[model_layer]

    def to_json(self):
        return {
            'images': [i.to_json() for i in self.image_refs]
        }

    class VersionNotFound(Exception):
        pass


class CustomImageSet:
    def __init__(self, image_refs):
        self.image_refs = image_refs

    def normalized_activations(self, *, model_layer):
        return activations_cache.get_normalized_activations(self.image_refs, model_layer=model_layer)


@lru_cache(maxsize=128)
def get_builtin_image_set(version_name):
    return BuiltInImageSet(version_name)
