# CAVlib

<!-- MARK intro start -->

![CAVlib banner](https://user-images.githubusercontent.com/1244307/140734434-43c012ec-c093-4400-b7a2-01cbac90295c.jpg)

CAVlib is a Python library that lets you use concept activation vectors ([CAVs]) in your own websites, apps and prototypes. It works with CAVs created in [Mood Board Search], or trained within CAVlib itself.

In only a few lines of code, CAVlib unlocks the power of meaningful visual AI interpretation for a host of potential new applications. CAVlib is designed to have a simple, Python API, that's usable by developers - no ML experience needed!

[CAVs]: https://arxiv.org/abs/1711.11279
[Mood Board Search]: https://github.com/google-research/mood-board-search

<!-- MARK intro end -->

## Installation

<!-- MARK installation start -->

CAVlib can be installed through pip.

```sh
$ pip install 'git+https://github.com/google-research/mood-board-search.git#egg=cavlib&subdirectory=cavlib'
```

CAVlib supports Python 3.7, 3.8, and 3.9, on macOS, Linux and Windows.

> **Note**: Due to limited availability of tflite-runtime wheels on
> PyPI, you might need to add an `--extra-index-url` argument to pip, like
> this:
>
> ```sh
> $ pip install --extra-index-url https://google-coral.github.io/py-repo/ 'git+https://github.com/google-research/mood-board-search.git#egg=cavlib&subdirectory=cavlib'

> ```

<!-- MARK installation end -->

## Developing

To work on CAVlib itself, clone this repo, and then:

```sh
# create and activate a venv
$ python3 -m venv env
$ source env/bin/activate

# install the dev dependencies
$ python -m pip install -r requirements-dev.txt

# check the types
$ mypy

# run the tests
$ pytest
```

## Sample programs that use CAVLib

<!-- MARK guide start -->

Here's a program that calculates the CAV score for a few images on your computer:

```python
from pathlib import Path
from cavlib import CAV

images_dir = Path('examples/images')
my_cav = CAV.load('examples/roundness.cav')

for image in images_dir.iterdir():
    print(image.name, my_cav.score(image))
```

Here's a program that searches a folder of images for the top 3 according a CAV:

```python
from pathlib import Path
from cavlib import CAV

images_dir = Path('examples/images')
image_files = list(images_dir.iterdir())

my_cav = CAV.load('examples/roundness.cav')
sorted_images = my_cav.sort(image_files, reverse=True)
print('top 3 images:', sorted_images[0:3])
```

Or here's a program that takes a CAV from CAVstudio and runs it on a live video feed from your webcam:

```python
import cv2
from cavlib import CAV

webcam = cv2.VideoCapture(0)
my_cav = CAV.load('examples/roundness.cav')

while True:
    _, frame = webcam.read()
    print(my_cav.score(frame))
    cv2.imshow('webcam', frame)
    cv2.waitKey(1)
```
These examples are also available in a [IPython notebook](examples/examples.ipynb).

<!-- MARK guide end -->

For more information on how to use CAVlib, take a look at the [API documentation](https://storage.googleapis.com/cavlib/87hf9s987hf90ashbf628nf0amsfhjakskf671bf/home.html).

## How can I send feedback or get in contact with you?

You have a few options:

- Email cav-experiments-support@google.com
- Submit your project to the [Experiments with Google] page

[Experiments with Google]: https://experiments.withgoogle.com/submit

## Contributors

This is not an official Google product, but an experiment that was a collaborative effort by friends from Nord Projects and Google Brain, Mural, and PAIR teams at Google.

- [Nord Projects](https://github.com/nordprojects)
- [Been Kim](https://github.com/BeenKim)
- [Emily Reif](https://github.com/EmilyReif)

## License

Copyright 2022 Google Inc.

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Final thoughts

We encourage open sourcing projects as a way of learning from each other. Please respect our and other creators’ rights, including copyright and trademark rights when present, when sharing these works and creating derivative work.

If you want more info on Google's policy, you can find that [here](https://policies.google.com/).
