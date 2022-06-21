These test activations were generated with the tensorflow/tcav repo, using the
script below.

The Mobilenet activations were created using cavlib itself, because tcav
doesn't have a model wrapper for MobilenetV1.

```
from tcav.activation_generator import ImageActivationGenerator
from tcav.model import GoogleNetWrapper_public
from tcav.utils import create_session
import numpy as np

sess = create_session()
model = GoogleNetWrapper_public(
    sess=sess,
    model_saved_path='tcav/tcav_examples/image_models/imagenet/inception5h/tensorflow_inception_graph.pb',
    labels_path='tcav/tcav_examples/image_models/imagenet/inception5h/imagenet_comp_graph_label_strings.txt'
)

ag = ImageActivationGenerator(
    model=model,
    source_dir='tcav/tcav_examples/image_models/imagenet',
    acts_dir='activations'
)

image = ag.load_image_from_file(
    filename='sample_images/0a8d36f893911e09a257cfaea8a8543a.1x.224x224.png',
    shape=(224, 224),
)

acts = model.run_examples(np.array([image]), 'mixed4d')
acts = model.reshape_activations(acts).squeeze().flatten()

np.save('sample_images/0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_4d.npy', acts)

acts = model.run_examples(np.array([image]), 'mixed5b')
acts = model.reshape_activations(acts).squeeze().flatten()

np.save('sample_images/0a8d36f893911e09a257cfaea8a8543a.1x.googlenet_5b.npy', acts)
```
