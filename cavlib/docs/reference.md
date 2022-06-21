# Reference

```{eval-rst}
.. currentmodule:: CAVlib
```

## Loading & using CAVs

The main way to use CAVlib is through the {class}`cavlib.CAV` class.

```{eval-rst}
.. autoclass:: cavlib.CAV
    :members:
```

## Training CAVs

```{eval-rst}
.. autofunction:: cavlib.train_cav

.. autoclass:: cavlib.TrainingImage
```

## Computing activations

```{eval-rst}
.. autofunction:: cavlib.compute_activations
```

(cavableimage)=

## Image formats

Images can be supplied to CAVlib in a number of formats, as denoted in the API
documentation as `CAVableImage`.

```{eval-rst}
.. describe:: CAVableImage

    Wherever ``CAVableImage`` appears, the following data types are accepted:

    * A path to an image file on disk, as a ``str`` or :class:`pathlib.Path`
    * A :class:`PIL.Image.Image` object, as loaded by Pillow using e.g.
      :func:`PIL.Image.open`
    * A numpy array containing RGB data, with shape (y, x, 3)

    Images that are not the correct size for the model (224, 244) will be:

    * center cropped so that they are square
    * bilinear resized to the correct dimensions
```

(model-layers)=

## Model layers

```{eval-rst}
.. describe:: ModelLayer

    Specifies the model and layer to use to train/evaluate CAVs.

    ``googlenet_4d``
        A layer mid-way through :class:`GooglenetModel`. In our testing, it's
        good at detecting distinct visual elements like shapes and patterns.

    ``googlenet_5b``
        A layer towards the end of :class:`GooglenetModel`. We have found it
        more conceptual layer that’s good at detecting diverse patterns,
        textures and compositions.

    ``mobilenet_12d``
        A layer within :class:`MobilenetModel` that’s good at detecting more
        obvious visual themes like colour and texture.
```

## Low-level

### Model API

```{eval-rst}
.. automodule:: cavlib.models
    :members:
    :undoc-members:
    :show-inheritance:
```
