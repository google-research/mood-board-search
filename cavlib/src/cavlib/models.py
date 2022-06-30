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

import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union

import numpy as np
from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter

from cavlib.utils import assert_shape
from cavlib.typing import NDArray

MODEL_LAYER_MOBILENET_12D = 'mobilenet_12d'
MODEL_LAYER_GOOGLENET_4D = 'googlenet_4d'
MODEL_LAYER_GOOGLENET_5B = 'googlenet_5b'

RESOURCES_DIR = Path(__file__).parent / 'resources'


class Model:
    '''
    Base class for models that can produce activations for CAVs.
    '''
    def __init__(self, model_path: Union[str, Path], input_value_range: Tuple[float, float]):
        self.interpreter = TFLiteInterpreter(model_path=str(model_path), num_threads=4)
        self.input_value_range = input_value_range

        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.lock = threading.Lock()

    @property
    def output_layer_names(self) -> List[str]:
        '''
        A list of layer names that can be used with
        :func:`get_activation_for_image` and
        :func:`get_multiple_activations_for_image`
        '''
        return [layer['name'] for layer in self.output_details]

    def get_activation_for_image(self, image: NDArray[Any], layer_name: str) -> NDArray[np.float32]:
        '''
        Returns an activation vector for a single image.

        :param numpy.ndarray image: a numpy array of shape (224, 244, 3), either in uint8
            type, in the range 0-255, or in floating point, from 0.0-1.0.
        :param layer_name: Layer name to return activations for.

        :return: the activation vector
        :rtype: numpy.ndarray
        '''
        activations_dict = self.get_multiple_activations_for_image(image, layer_names=[layer_name])
        return activations_dict[layer_name]

    def get_multiple_activations_for_image(self, image: NDArray[Any], layer_names: List[str]) -> Dict[str, NDArray[np.float32]]:
        '''
        Returns multiple layer activations for a single image. Faster than
        get_activations_for_image because the model is only run once.

        :param numpy.ndarray image: a numpy array of shape (224, 244, 3), either in uint8
            type, in the range 0-255, or in floating point, from 0.0-1.0.
        :param layer_names: Layer names to return activations for.

        :return: List of dicts, containing {layer_name: activation}
        :rtype: Dict[str, numpy.ndarray]
        '''

        if image.dtype == np.uint8:
            image = image.astype(np.float32) / 255
        elif image.dtype in [np.float16, np.float64]:
            image = image.astype(np.float32)
        elif image.dtype == np.float32:
            pass
        else:
            raise TypeError('image is an unsupported dtype.')

        # print('min', image.min(), 'max', image.max())

        # scale input
        low, high = self.input_value_range
        image = (image * (high - low)) + low  # type: ignore

        # reshape image to fit the input tensor
        image = image.reshape((1, 224, 224, 3))

        with self.lock:
            input_shape = self.input_details[0]['shape']

            assert_shape(image, input_shape)

            self.interpreter.set_tensor(self.input_details[0]['index'], image)

            self.interpreter.invoke()

            result = {}

            for layer_name in layer_names:
                try:
                    output_layer_info = next(l for l in self.output_details if l['name'] == layer_name)
                except StopIteration:
                    raise ValueError(f'Unknown layer name: {layer_name}')

                output_data = self.interpreter.get_tensor(output_layer_info['index'])

                # flatten the activation to a single vector
                output_data = output_data.reshape(-1)

                result[layer_name] = output_data

        return result


class GooglenetModel(Model):
    '''
    The model architecture known as 'GoogLeNet' or 'Inception v1'. This
    particular model was pretrained on ImageNet, and was released by Google
    under the name 'inception5h'.
    '''
    def __init__(self) -> None:
        super().__init__(
            model_path=RESOURCES_DIR / 'google_net_inception_v1.tflite',
            input_value_range=(-117, 255 - 117),
        )


class MobilenetModel(Model):
    '''
    Mobilenet v1, pretrained on ImageNet.
    '''
    def __init__(self) -> None:
        super().__init__(
            model_path=RESOURCES_DIR / 'mobilenet_v1_1.0_224.tflite',
            input_value_range=(0, 1),
        )
