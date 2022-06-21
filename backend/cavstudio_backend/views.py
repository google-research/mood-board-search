import io
import os

import numpy as np
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .cav import CAV
from .image_reference import ImageReference, TrainingImageReference, injest_image
from .ml_engine import MODEL_LAYERS
from .ml_image import MLImage
from .image_set import BuiltInImageSet, get_builtin_image_set, CustomImageSet
from .utils import parse_data_uri, serialize_data_uri

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@api_view(['POST'])
def upload_image(request):
    data224, _ = parse_data_uri(request.data['data224'])
    data1200, _ = parse_data_uri(request.data['data1200'])

    image = injest_image(
        image_data_224=data224, image_data_1200=data1200, user_generated=True
    )

    return Response(image.to_json())


@api_view(['POST'])
def generate_cav(request):
    positive_image_refs = [TrainingImageReference.from_json(i) for i in request.data['positive_images']]
    negative_image_refs = [TrainingImageReference.from_json(i) for i in request.data['negative_images']]
    model_layer = request.data['model_layer']
    search_set_name = request.data['search_set']

    if model_layer not in MODEL_LAYERS:
        raise ParseError('unknown model_layer')

    if search_set_name == 'custom':
        # the search_images uses a custom JSON structure - just a list of
        # dicts with ids, to keep the request size down.
        search_image_refs = [ImageReference(id=i['id'], user_generated=True)
                             for i in request.data['search_images']]
        search_set = CustomImageSet(search_image_refs)
    else:
        try:
            search_set = get_builtin_image_set(search_set_name)
        except BuiltInImageSet.VersionNotFound:
            raise ParseError('unknown scout version name')

    cav = CAV.learn_from(
        positive_image_refs=positive_image_refs,
        negative_image_refs=negative_image_refs,
        model_layer=model_layer,
    )

    search_set_activations = search_set.normalized_activations(model_layer=model_layer)

    # use dot product of prenormalised activations to improve performance
    # (dot product of normalised vectors is the same as cosine similarity)
    search_set_scores = np.dot(search_set_activations, cav.vector)

    # sort descending
    search_sort_indexes = (-search_set_scores).argsort()

    # get top images
    top_image_indexes = search_sort_indexes[0:100]

    top_image_refs = [search_set.image_refs[idx] for idx in top_image_indexes]
    top_image_scores = [search_set_scores[idx] for idx in top_image_indexes]

    cav.update_stats_from_scores(search_set_scores)
    cav.save()

    return Response({
        'result_images': [i.to_json() for i in top_image_refs],
        'result_scores': top_image_scores,
        'cav_string': cav.summary_string(max_length=500),
        'cav_id': cav.id,
        'cav_score_stats': cav.stats.to_dict()
    })


@api_view()
def image_set(request, name):
    try:
        image_set = get_builtin_image_set(name)
    except BuiltInImageSet.VersionNotFound:
        raise Http404

    return Response(image_set.to_json())


@api_view(['POST'])
def inspect(request):
    image_ref = ImageReference.from_json(request.data['image'])
    cav_id = request.data['cav_id']
    cav = CAV.load(cav_id)

    ml_image = MLImage.load(image_ref.image_224_path)
    heatmap_image = ml_image.get_crop_heatmap(cav)

    heatmap_image_png_io = io.BytesIO()
    heatmap_image.save(heatmap_image_png_io, format='png')

    top_crop = ml_image.get_top_crop(cav)

    return Response({
        'heatmap': serialize_data_uri(heatmap_image_png_io.getvalue(), mime_type='image/png'),
        'top_crop': top_crop.to_crop_spec_json(),
    })


@api_view(['POST'])
def crops(request):
    image_ref = ImageReference.from_json(request.data['image'])
    cav_id = request.data['cav_id']
    cav = CAV.load(cav_id)

    ml_image = MLImage.load(image_ref.image_224_path)
    crops, scores = ml_image.top_crops_and_scores(cav)

    return Response({
        'top_crop': crops[0].to_crop_spec_json(),
        'crops': [c.to_crop_spec_json() for c in crops],
        'scores': scores,
    })


@api_view(['POST'])
def heatmap(request):
    ''' Version of inspect which only does heatmap '''
    image_ref = ImageReference.from_json(request.data['image'])
    cav_id = request.data['cav_id']
    cav = CAV.load(cav_id)

    ml_image = MLImage.load(image_ref.image_224_path)
    heatmap_image = ml_image.get_crop_heatmap(cav)

    heatmap_image_png_io = io.BytesIO()
    heatmap_image.save(heatmap_image_png_io, format='png')

    return Response({
        'heatmap': serialize_data_uri(heatmap_image_png_io.getvalue(), mime_type='image/png'),
    })


@api_view()
def ping(request):
    return Response()
