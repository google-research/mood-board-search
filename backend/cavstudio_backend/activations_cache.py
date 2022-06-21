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
