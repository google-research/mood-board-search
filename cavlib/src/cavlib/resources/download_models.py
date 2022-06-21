import tempfile
import textwrap
import sys
from urllib.request import urlretrieve
import shutil
from pathlib import Path

try:
    import tensorflow as tf
except ImportError:
    import traceback
    traceback.print_exc()
    sys.exit('This script requires tensorflow. Install with "pip install tensorflow"')

INCEPTION5H_URL = 'https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip'
MOBILENET_V1_URL = 'https://storage.googleapis.com/download.tensorflow.org/models/mobilenet_v1_2018_02_22/mobilenet_v1_1.0_224.tgz'
RESOURCES_DIR = Path(__file__).parent

def main() -> None:
    print(textwrap.dedent('''
        This script downloads the models for CAVlib, converts them for tflite
        and bundles them into the repo.
    '''))

    if input('Continue [y/N]: ') != 'y':
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_path_str:
        temp_dir = Path(tmp_path_str)
        inception_zip = temp_dir / 'inception5h.zip'

        print('Downloading', INCEPTION5H_URL)

        urlretrieve(INCEPTION5H_URL, inception_zip)
        inception_folder = temp_dir / 'inception5h'

        print('Unpacking archive...')
        shutil.unpack_archive(inception_zip, extract_dir=inception_folder)

        print('Converting to TFLite...')
        inception_model = inception_folder / 'tensorflow_inception_graph.pb'
        converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
            graph_def_file=inception_model,
            input_arrays=['input'],
            output_arrays=[
                'mixed3a', 'mixed3b',
                'mixed4a', 'mixed4b', 'mixed4c', 'mixed4d', 'mixed4e',
                'mixed5a', 'mixed5b'
            ],
            input_shapes={
                "input": (1, 224, 224, 3),
            }
        )
        inception_model_tflite = RESOURCES_DIR / 'google_net_inception_v1.tflite'
        with open(inception_model_tflite, 'wb') as f:
            f.write(converter.convert())

        shutil.copy(
            inception_folder / 'LICENSE',
            RESOURCES_DIR / 'google_net_inception_v1.license.txt'
        )

        print('Downloading', MOBILENET_V1_URL)

        mobilenet_zip = temp_dir / 'mobilenet_v1_1.0_224.tgz'
        urlretrieve(MOBILENET_V1_URL, mobilenet_zip)
        mobilenet_folder = temp_dir / 'mobilenet5h'

        print('Unpacking archive...')
        shutil.unpack_archive(mobilenet_zip, extract_dir=mobilenet_folder)

        print('Converting to TFLite...')
        mobilenet_model = mobilenet_folder / 'mobilenet_v1_1.0_224_frozen.pb'
        converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
            graph_def_file=mobilenet_model,
            input_arrays=['input'],
            output_arrays=[
                'MobilenetV1/MobilenetV1/Conv2d_2_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_4_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_4_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_5_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_5_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_6_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_6_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_7_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_7_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_8_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_8_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_9_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_9_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_10_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_10_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_11_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_11_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_12_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_12_pointwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_13_depthwise/Relu6',
                'MobilenetV1/MobilenetV1/Conv2d_13_pointwise/Relu6'],
            input_shapes={
                "input": (1, 224, 224, 3),
            }
        )
        mobilenet_model_tflite = RESOURCES_DIR / 'mobilenet_v1_1.0_224.tflite'
        with open(mobilenet_model_tflite, 'wb') as f:
            f.write(converter.convert())

        urlretrieve(
            'https://github.com/tensorflow/models/raw/master/LICENSE',
            RESOURCES_DIR / 'mobilenet_v1_1.0_224.license.txt'
        )

if __name__ == '__main__':
    main()
