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

import base64
import re
from typing import Type

import numpy as np
import PIL.Image
import PIL.ImageColor


DATA_URI_REGEX = re.compile(
    r'''
    ^data: # header
    ([-\w.]+/[-\w.]+); # capture mime type
    base64, # encoding (only base64 supported)
    (.*) # capture the rest of the string
    $
    ''',
    re.VERBOSE
)


def parse_data_uri(data_uri):
    match = DATA_URI_REGEX.match(data_uri)

    mime_type = match.group(1)
    base64_data = match.group(2)
    data = base64.b64decode(base64_data)

    return data, mime_type


def serialize_data_uri(data, mime_type):
    return b'data:%b;base64,%b' % (bytes(mime_type, 'ascii'), base64.b64encode(data))


class ArrayShapeError(TypeError):
    pass


def assert_shape(x: np.ndarray, shape: tuple):
    """ e.g.: assert_shape(conv_input_array, [8, 3, None, None]) """
    if not shape_equal(x, shape):
        x_shape = np.shape(x)
        raise ArrayShapeError(f'Argument has the incorrect shape. Expected {shape}, received {x_shape}.')


def shape_equal(x: np.ndarray, shape: tuple) -> bool:
    """ e.g.: shape_equal(conv_input_array, [8, 3, None, None]) """
    x_shape = np.shape(x)
    if len(x_shape) != len(shape):
        return False

    for _a, _b in zip(x_shape, shape):
        if isinstance(_b, int):
            if _a != _b:
                return False
    return True


def split_into_chunks(seq, chunk_size):
    for i in range(0, len(seq), chunk_size):
        chunk = seq[i:i+chunk_size]
        yield chunk


def rotate_image_by_exif_tag(pil_image):
    '''
    PIL.ImageOps.exif_transpose() crashes for our cavscout images, for some
    reason. This function works around those problems.
    '''
    exif = pil_image.getexif()
    orientation = exif.get(0x0112)

    method = {
        2: PIL.Image.FLIP_LEFT_RIGHT,
        3: PIL.Image.ROTATE_180,
        4: PIL.Image.FLIP_TOP_BOTTOM,
        5: PIL.Image.TRANSPOSE,
        6: PIL.Image.ROTATE_270,
        7: PIL.Image.TRANSVERSE,
        8: PIL.Image.ROTATE_90,
    }.get(orientation)

    if method is not None:
        transposed_image = pil_image.transpose(method)
        del transposed_image.info["exif"]
        return transposed_image

    return pil_image.copy()


def parse_hex_color(hex_color):
    '''
    Input: string e.g. "#ab7afc"
    Output: array of floats in range 0-1 e.g. [0.676, 0.483, 0.998]
    '''
    return [c/255.0 for c in PIL.ImageColor.getrgb(hex_color)]

