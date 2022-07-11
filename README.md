# Mood Board Search

![Hero image](https://user-images.githubusercontent.com/1244307/140734553-0f812a63-0857-4039-a9dd-0094dab62a65.jpg)

## What is Mood Board Search?

Mood Board Search is an A.I. Experiment that lets you train a computer to recognize visual concepts using mood boards and machine learning. It’s a playful way to explore and analyze image collections using mood boards as your search query.

For this release, we're making Mood Board Search available as a HTML/JS frontend app (“CAVstudio”)  that works with a local Python backend.

## Who is it for?

Artists, photographers, image researchers, curators, educators – really, anyone who wants to work with images in more expressive and subjective ways.

## What is this repository for?

This repository contains two components related to Mood Board Search:

- “CAVstudio”
- “CAVlib”

## How does Mood Board Search work?

![Tech diagram](https://user-images.githubusercontent.com/1244307/140048774-974b455a-0a29-4e78-a1ed-5a42960f40df.png)

Mood Board Search works by training a model to recognize a visual concept using an open-source ML method called [concept activation vectors (CAVs)]. Once you’ve trained your CAV, you can use it to search image collections to show you the closest matches, according to your CAV. You can review the results, fine-tune the things it likes, and inspect each result to understand what it's drawn to. Once you’re finished training a CAV, you can deploy it into a Python application using only a few lines of code.


CAVstudio works by creating a concept activation vector (CAV) from your training images, and then using it to search a set of images to show you the closest matches according to the CAV. You can review the results, fine tune the things it likes, and inspect each result to understand what it's drawn to.

Once you're happy, you can export the CAV file for use in [CAV Camera](https://play.google.com/store/apps/details?id=co.nordprojects.cavcam), or use it in your own projects with [CAVlib].

[concept activation vectors (CAVs)]: https://arxiv.org/abs/1711.11279

## A closer look at CAVs

<!-- MARK how it works start -->

CAVs are a direction in 'embedding space' - a vector. It works like this: if you take a layer of a neural network ML model and extract all the values in the neurons at that point (the 'activations'), you can treat these values as a point in embedding space. Every different input image is mapped to a different location, with similar images close together, and different images far apart.

---

![Embedding Projector](https://user-images.githubusercontent.com/1244307/140049984-eb640d03-a2e8-44b3-9ec4-b337e03524a7.png)

<center><small><i>'Embedding space' is a high-dimensional space - perhaps thousands of dimensions. <a href="https://projector.tensorflow.org/">Embedding projector</a> is a visual way to explore embedding spaces, by projecting each point to 3 dimensions using clever mathematical techniques like UMAP and T-SNE.</i></small></center>

---

CAVs can be used as a lightweight way to train neural network ML models to recognise new visual concepts.  By taking existing pretrained models, CAVs can expose hidden understanding of inner layers of the model by finding the direction (a.k.a 'vector') of a concept in the high-dimensional embedding space. This is a simple form of transfer learning that produces surprisingly good results with tiny amounts of training data. We've had success training CAVs using as few as 10-30 images. The resulting CAV is very lightweight - around 250kB - and can be deployed into a Python application using only a few lines of code.

To create a CAV, you need positive and negative training images. Positive images show the concept you're trying to express, and negative ones do not (or even better, show the opposite).

For example, if you were trying to create a CAV to illustrate a concept 'roundness', your positive training images would be pictures of round things, and the negative images would be not-round things, or just random images.

CAVs are created by finding a direction in this high dimensional space that differentiates the positive from the negative training images. You can train (and download) a CAV from Mood Board Search, or train it directly in CAVlib using the cavlib.train_cav function.

Once formed, the CAV can be compared with any new image, by looking at the angle between the CAV and the new image's activations, a technique known as cosine similarity. We call the resulting number the 'CAV score' - in our example, a measure of 'roundness' - as a number from -1 to 1.

![Diagram](https://user-images.githubusercontent.com/1244307/140050379-d98bff8a-15b0-4b36-ac83-e6a5bd3efc13.png)

<!-- MARK how it works end -->

## How to use Mood Board Search

This release of Mood Board Search is available as a HTML/JS frontend app (“CAVstudio”) that works with a local Python backend.

To run CAVstudio, you'll need on your machine:
- Python 3.8. You can download it from [Python.org](https://www.python.org/downloads/).
- node v15+. Download it from [nodejs.org](https://nodejs.org/en/download/). We used node v15, but newer versions should also work.

### Setup

First, clone this repository.

There are two servers that make Mood Board Search. The backend Python server manages the data store and runs the ML algorithms. The frontend server builds and hosts the browser-based user interface.

To set up the backend:

    cd backend

    python -m venv env
    .env\bin\activate
    pip install -U pip
    pip install -r requirements.txt
    python -m pip install Django
    pip install tqdm numpy Pillow cached-property
    
    
    cd ..
    pip install --extra-index-url https://google-coral.github.io/py-repo/ .\cavlib
    cd backend
    pip install platformdirs djangorestframework django-cors-headers 

Finally, download a sample set of images to work from. This script downloads two files:

1. A sample set that contains 2700 photos (.jpgs and .pngs) of everyday things—from household objects to plants and animals to local monuments and landmarks—taken by people from a Google design team. Photos were taken by a phone camera. EXIF data were removed from all images and all images are shared under [the Creative Commons CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/). Please note: These images were collected specifically to demonstrate the functionality of the Mood Board Search tool. The Mood Board Search tool selects images from this gallery based on a set of inputs. We do not expect people to use the images for any other purpose. This gallery of images was not constructed for the purposes of training machine learning models. Therefore, no scientific tests were conducted on this gallery of images. The Mood Board tool is based on [technology](https://github.com/tensorflow/tcav) developed by Google Researchers (Been Kim and colleagues). See [paper](https://arxiv.org/abs/1711.11279) for details. This will download 1.1GB of data onto your device, taking around 10-15 mins (depending on your connection & compute speeds).

2. Sample visual concepts by Alex Etchells, Tom Hatton, and Rachel Maggart. The images contained within the visual concepts are made publicly available for use in Mood Board Search (“CAVstudio”) only. The owners of the images retain copyright.

```
python bin/download_data.py
```

The backend is now ready to go.

    cd ..

Next, set up the frontend:

    cd frontend
    npm install -g @vue/cli
    npm ci

### Running

Once you're all set up, you can start the two servers to use CAVstudio.

To run the backend, open one terminal window and do:

    cd backend
    python manage.py runserver

In another terminal window, run the frontend server:

    cd frontend
    npm run serve

Then go to http://localhost:8080 in a browser to use CAVstudio.

Explore three preloaded concepts, or create a new concept using images from your computer.

To create a new concept:

1. Gather and upload images that evoke a certain style, mood, or “feel” of an idea. We recommend using 50 square-ratio  images, but we’ve had success using as few as 15 images.
2. Select an image set to search.
3. Train your Concept Activation Vector (CAV) and explore the results to see how well the model expresses your concept.
4. Inspect your results using Focus mode to see which parts of the image match your mood board best – or AI crop mode, to crop in directly to uncover new compositions.
5. You can retrain your CAV as many times as you like by upweighting, downweighting, deleting, or adding new images to your mood board.
6. Once you're happy with how the model expresses your visual concept, you can download your CAV file for use in [CAVcamera], an experimental camera app we made that lets you take photos using CAVs as your real-time guide.

[CAVcamera]: https://play.google.com/store/apps/details?id=co.nordprojects.cavcam

Want to use Mood Board Search in your own website creations? We’ve made a library called [CAVlib] that lets you do just that.

[CAVlib]: ./cavlib

## How can I send feedback or get in contact with you?

You have a few options:

- Email cav-experiments-support@google.com
- Submit your project to the [Experiments with Google] page

[Experiments with Google]: https://experiments.withgoogle.com/submit

## Contributors

This is not an officially supported Google product, but an experiment that was a collaborative effort by friends from Nord Projects and Google Brain, Mural, and PAIR teams at Google.

- [Nord Projects](https://github.com/nordprojects)
- [Been Kim](https://github.com/BeenKim)
- [Emily Reif](https://github.com/EmilyReif)

## License

Copyright 2022 Google LLC.

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND", either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Final thoughts

We encourage open sourcing projects as a way of learning from each other. Please respect our and other creators’ rights, including copyright and trademark rights when present, when sharing these works and creating derivative work.

If you want more info on Google's policy, you can find that [here](https://policies.google.com/).
