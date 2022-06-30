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

# We can't do anything about the deprecation warnings, since TCAV runs on
# Tensorflow 1.x, so I'm silencing them for now.
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from cached_property import threaded_cached_property as cached_property

from .utils import assert_shape
from cavlib.models import GooglenetModel, MobilenetModel, Model
from pathlib import Path

MODEL_LAYER_MOBILENET_12D = 'mobilenet_12d'
MODEL_LAYER_GOOGLENET_4D = 'googlenet_4d'
MODEL_LAYER_GOOGLENET_5B = 'googlenet_5b'

MODEL_LAYERS = [
    MODEL_LAYER_MOBILENET_12D,
    MODEL_LAYER_GOOGLENET_4D,
    MODEL_LAYER_GOOGLENET_5B,
]



class MLEngine(object):
    def __init__(self):
        pass

    @cached_property
    def mobilenet_model(self) -> Model:
        return MobilenetModel()

    @cached_property
    def googlenet_model(self) -> Model:
        return GooglenetModel()

    def model_for_model_layer(self, model_layer: str) -> Model:
        if model_layer.startswith('mobilenet_'):
            return self.mobilenet_model
        if model_layer.startswith('googlenet_'):
            return self.googlenet_model
        raise Exception('unknown model_layer')

    def layer_name_for_model_layer(self, model_layer: str):
        if model_layer == MODEL_LAYER_MOBILENET_12D:
            return 'MobilenetV1/MobilenetV1/Conv2d_12_depthwise/Relu6'
        if model_layer == MODEL_LAYER_GOOGLENET_4D:
            return 'mixed4d'
        if model_layer == MODEL_LAYER_GOOGLENET_5B:
            return 'mixed5b'

    def calculate_activations(self, model_layers, images) -> list:
        '''
            Args:
                model_layers (list): List of model layer identifiers
                images (list): List of numpy arrays of shape (224, 244, 3)

            Returns:
                List of dicts, containing {model_layer: numpy.ndarray}

            Avoid calling with a lot of images. If many are needed, chunk input into 20 and call with each in turn.
        '''
        if len(images) == 0:
            return []

        assert_shape(images, (None, 224, 224, 3))

        # get the results dicts ready
        results = [{} for _ in images]

        for model in [self.googlenet_model, self.mobilenet_model]:
            model_layers_for_this_model = [m for m in model_layers if self.model_for_model_layer(m) == model]

            if len(model_layers_for_this_model) == 0:
                continue

            layer_names = [self.layer_name_for_model_layer(m) for m in model_layers_for_this_model]

            for i, image in enumerate(images):
                activations = model.get_multiple_activations_for_image(image=image, layer_names=layer_names)

                for model_layer in model_layers_for_this_model:
                    layer_name = self.layer_name_for_model_layer(model_layer)
                    results[i][model_layer] = activations[layer_name].reshape(-1)

        return results


ml_engine = MLEngine()
