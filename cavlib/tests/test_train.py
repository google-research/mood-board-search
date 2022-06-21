import random
import numpy as np

import pytest

from cavlib import train_cav

from .utils import TEST_DATA_DIR

CAV_DIR = TEST_DATA_DIR / 'sample_cav'

POSITIVE_IMAGES = list((CAV_DIR / 'training_positive').glob("*.png"))
NEGATIVE_IMAGES = list((CAV_DIR / 'training_negative').glob("*.png"))
RESULT_IMAGES = list((CAV_DIR / 'results').glob("*.png"))

@pytest.mark.parametrize('model_layer', ['googlenet_4d', 'googlenet_5b', 'mobilenet_12d'])
def test_train_and_sort(model_layer):
    # training CAVs is non-deterministic due to the use of SGDClassifier.
    # seed the RNG and sort the training data to produce consistent results.
    cav = train_cav(
        positive_images=sorted(POSITIVE_IMAGES),
        negative_images=sorted(NEGATIVE_IMAGES),
        model_layer=model_layer,
        random_state=np.random.RandomState(1234)
    )

    images_to_sort = RESULT_IMAGES.copy()
    random.shuffle(images_to_sort)

    sorted_images = cav.sort(images_to_sort, reverse=True)

    # check that the initial order had nothing to do with it
    images_to_sort.reverse()

    sorted_images_2 = cav.sort(images_to_sort, reverse=True)

    assert sorted_images == sorted_images_2

    sorted_image_names = [im.name for im in sorted_images]

    if model_layer == 'googlenet_4d':
        # this CAV was created on googlenet 4d, so it should return results in
        # that order
        assert sorted_image_names == ['1.png', '2.png', '3.png', '4.png', '5.png']
    elif model_layer == 'googlenet_5b':
        # different models see things slightly differently, but generally
        # agree
        assert sorted_image_names == ['1.png', '2.png', '4.png', '5.png', '3.png']
    elif model_layer == 'mobilenet_12d':
        assert sorted_image_names == ['1.png', '2.png', '3.png', '5.png', '4.png']
    else:
        assert False
