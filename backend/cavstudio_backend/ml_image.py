from collections import namedtuple
from methodtools import lru_cache

import numpy as np
import PIL.Image
import skimage.transform
import sklearn.preprocessing

from cavstudio_backend.utils import assert_shape, parse_hex_color
from cavstudio_backend.ml_engine import ml_engine
from cavstudio_backend.cav import CAV

heatmap_colormap = np.array([
    # format is:
    # stop_pos, r, g, b
    [0.00] + parse_hex_color('#000003'),
    [0.12] + parse_hex_color('#1F114B'),
    [0.24] + parse_hex_color('#4F117B'),
    [0.36] + parse_hex_color('#822581'),
    [0.49] + parse_hex_color('#B3357A'),
    [0.62] + parse_hex_color('#E55063'),
    [0.75] + parse_hex_color('#FB8861'),
    [1.00] + parse_hex_color('#FBFCBF'),
    [1.50] + parse_hex_color('#FFFFFF'),  # extra element for overshoots
])


class MLImageCrop:
    def __init__(self, center, zoom_level, pixels, activations_dict=None):
        self.center = center
        self.zoom_level = zoom_level
        self.pixels = pixels
        self.activations_dict = activations_dict or {}

    @property
    def dimension(self):
        return 1 / self.zoom_level

    @staticmethod
    def calculate_activations(crops, model_layer):
        crops_needing_activations = [c for c in crops if model_layer not in c.activations_dict]

        activations_dicts = ml_engine.calculate_activations(
            model_layers=[model_layer],
            images=[c.pixels for c in crops_needing_activations]
        )

        # store the activations on the image so they can be used later
        for crop, activations_dict in zip(crops_needing_activations, activations_dicts):
            crop.activations_dict = activations_dict

    def to_crop_spec_json(self):
        return {
            'x': self.center[0] - self.dimension/2,
            'y': self.center[1] - self.dimension/2,
            'width': self.dimension,
            'height': self.dimension,
        }


class MLImage:
    pixels: np.ndarray
    image: PIL.Image.Image

    @classmethod
    def load(cls, image_224_path):
        return cls(PIL.Image.open(image_224_path))

    def __init__(self, image):
        self.image = image

        assert self.image.size[0] == 224 and self.image.size[1] == 224
        assert self.image.mode == 'RGB'

        self.pixels = np.array(image)
        assert_shape(self.pixels, (224, 224, 3))

    @property
    def width(self):
        return self.pixels.shape[0]

    @property
    def height(self):
        return self.pixels.shape[1]

    def get_crop_heatmap(self, cav: CAV):
        crops = []
        zoom_levels = [3, 4, 5, 6]

        for zoom_level in zoom_levels:
            for center in self.square_checkerboard_centers(zoom_level):
                crops.append(self.cropped_image(
                    center=center,
                    zoom_level=zoom_level,
                ))

        MLImageCrop.calculate_activations(crops, model_layer=cav.model_layer)
        activations = [c.activations_dict[cav.model_layer] for c in crops]

        activations = sklearn.preprocessing.normalize(activations, copy=False)
        scores = np.dot(activations, cav.vector)

        heatmap = np.zeros((224, 224), dtype=np.float32)

        for crop, score in zip(crops, scores):
            bbox = self.bbox(crop.center, crop.zoom_level)
            heatmap[bbox[2]:bbox[3], bbox[0]:bbox[1]] += score

        heatmap /= len(zoom_levels)

        if cav.stats is None:
            raise Exception('cav stats required to render heatmap')

        # scale so that mean is 0 and a very high score is 1
        heatmap = (heatmap - cav.stats.mean) / (cav.stats.top_5_mean - cav.stats.mean)

        # convert to image color using colormap
        colormap_stops = heatmap_colormap[:, 0]
        colormap_colors = heatmap_colormap[:, 1:4]

        # interp each channel separately
        image_array = np.stack(
            [
                np.interp(heatmap, colormap_stops, colormap_colors[:, 0]),
                np.interp(heatmap, colormap_stops, colormap_colors[:, 1]),
                np.interp(heatmap, colormap_stops, colormap_colors[:, 2]),
            ],
            axis=-1,
        )

        return PIL.Image.fromarray(np.uint8(image_array * 255), 'RGB')

    def top_crops_and_scores(self, cav):
        crop_specs = [
            ((1/2, 1/2), 1),

            ((3/8, 3/8), 4/3),
            ((5/8, 3/8), 4/3),
            ((5/8, 5/8), 4/3),
            ((3/8, 5/8), 4/3),

            ((1/4, 1/4), 2),
            ((2/4, 1/4), 2),
            ((3/4, 1/4), 2),
            ((1/4, 2/4), 2),
            ((2/4, 2/4), 2),
            ((3/4, 2/4), 2),
            ((1/4, 3/4), 2),
            ((2/4, 3/4), 2),
            ((3/4, 3/4), 2),
        ]
        crops = [self.cropped_image(center, zoom) for center, zoom in crop_specs]
        MLImageCrop.calculate_activations(crops, model_layer=cav.model_layer)
        activations = [c.activations_dict[cav.model_layer] for c in crops]

        activations = sklearn.preprocessing.normalize(activations, copy=False)
        scores = np.dot(activations, cav.vector)
        sorting_indexes = (-scores).argsort()

        sorted_crops = [crops[i] for i in sorting_indexes]
        sorted_scores = [scores[i] for i in sorting_indexes]

        return sorted_crops, sorted_scores

    def get_top_crop(self, cav):
        sorted_crops, _ = self.top_crops_and_scores(cav)
        return sorted_crops[0]

    def square_checkerboard_centers(self, zoom_level):
        # width = height = dimension
        dimension = 1/float(zoom_level)

        for x in range(zoom_level):
            for y in range(zoom_level):
                yield (
                    x*dimension + dimension/2,
                    y*dimension + dimension/2,
                )

    @lru_cache(128)
    def cropped_image(self, center: tuple, zoom_level) -> MLImageCrop:
        bbox = self.bbox(center, zoom_level)

        small_cropped_image = self.pixels[bbox[2]:bbox[3], bbox[0]:bbox[1], :]
        pixels = skimage.transform.resize(small_cropped_image, (224, 224), order=3)

        return MLImageCrop(center=center, zoom_level=zoom_level, pixels=pixels)

    def bbox(self, center, zoom_level):
        src_width = self.width / float(zoom_level)
        src_height = self.height / float(zoom_level)

        src_center_x = center[0] * self.width
        src_center_y = center[1] * self.height

        left = int(round(src_center_x - src_width/2))
        right = int(round(src_center_x + src_width/2))
        top = int(round(src_center_y - src_height/2))
        bottom = int(round(src_center_y + src_height/2))

        return (left, right, top, bottom)
