from pathlib import Path
import numpy as np

TEST_DATA_DIR = Path(__file__).parent / 'test_data'
TEST_IMAGE = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.224x224.png'
TEST_IMAGE_ACTIVATIONS_GOOGLENET_4D = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_4d.npy'
TEST_IMAGE_ACTIVATIONS_GOOGLENET_5B = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_5b.npy'
TEST_IMAGE_ACTIVATIONS_MOBILENET_12D = TEST_DATA_DIR / '0a8d36f893911e09a257cfaea8a8543a.1x.mobilenet_12d.npy'


def cosine_similarity(arr1, arr2):
    return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
