import time

from cavstudio_db.models import SearchSet, Snapshot
from cavstudio_db.serializers import SearchSetSerializer, SnapshotSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


@api_view()
def get_all_snapshots_for_project_including_snapshot(request):
    snapshot_id = request.query_params['snapshotId']
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)

    projectId = snapshot.data['projectId']
    snapshots = Snapshot.objects.raw('''
        SELECT cavstudio_db_snapshot.*
        FROM cavstudio_db_snapshot,
             json_each(cavstudio_db_snapshot.data, "$.projectId") AS project_id
        WHERE project_id.value=%s
    ''', [projectId])

    snapshots = sorted(snapshots, key=lambda s: s.data.get('date'), reverse=True)

    snapshots_json = SnapshotSerializer(snapshots, many=True).data
    return Response({'results': snapshots_json})


@api_view()
def get_user_projects_summary(request):
    snapshots = list(Snapshot.objects.all())

    # filter out the featured concepts
    snapshots = [s for s in snapshots if not s.data.get('featured')]

    snapshots.sort(key=lambda s: s.data['date'], reverse=True)

    project_ids = set(s.data['projectId'] for s in snapshots)
    projects_json = []

    for project_id in project_ids:
        # latestSnapshot = snapshots.filter(s => s.projectId === projectId)[0]
        latest_snapshot = next(s for s in snapshots if s.data['projectId'] == project_id)

        if latest_snapshot.data.get('deleted'):
            continue

        try:
            images = latest_snapshot.data['positiveSet']['images'] or []
        except KeyError:
            images = []

        top_images = sorted(images, key=lambda i: i['weight'], reverse=True)[:3]

        projects_json.append({
            'id': project_id,
            'latestSnapshot': {
                'id': latest_snapshot.id,
                'date': latest_snapshot.data['date'],
                'name': latest_snapshot.data['name'],
                'creatorName': latest_snapshot.data['creatorName'],
                'publishInfo': latest_snapshot.data['publishInfo'],
                'topImages': top_images,
            }
        })

    return Response({'results': projects_json})


@api_view()
def get_snapshot(request):
    snapshot_id = request.data['snapshotId']

    snapshot = get_object_or_404(Snapshot, id=snapshot_id)

    snapshot_json = SnapshotSerializer(snapshot).data

    return Response({'result': snapshot_json})


@api_view(['POST'])
def set_snapshot(request):
    snapshot_id = request.data['snapshotId']
    snapshot = request.data['snapshot']

    Snapshot.objects.update_or_create(id=snapshot_id, defaults={'data': snapshot})

    return Response()


@api_view(['POST'])
def delete_snapshot(request):
    snapshot_id = request.data['snapshotId']

    snapshot = get_object_or_404(Snapshot, id=snapshot_id)

    snapshot.data['deleted'] = True
    snapshot.data['deletedDate'] = time.time()

    snapshot.save()

    return Response()


@api_view()
def get_search_sets(request):
    search_sets = [s for s in SearchSet.objects.all() if not s.data.get('deleted')]

    search_sets_json = SearchSetSerializer(search_sets, many=True).data

    return Response({'results': search_sets_json})


@api_view()
def get_search_set(request):
    search_set_id = request.query_params['searchSetId']

    search_set = get_object_or_404(SearchSet, id=search_set_id)

    search_set_json = SearchSetSerializer(search_set).data

    return Response({'result': search_set_json})


@api_view(['POST'])
def set_search_set(request):
    search_set_id = request.data['searchSetId']
    search_set_data = request.data['searchSet']

    SearchSet.objects.update_or_create(id=search_set_id, defaults={'data': search_set_data})

    return Response()


@api_view(['POST'])
def delete_search_set(request):
    search_set_id = request.data['searchSetId']

    search_set = get_object_or_404(SearchSet, id=search_set_id)

    search_set.data['deleted'] = True
    search_set.data['deletedDate'] = time.time()

    search_set.save()

    return Response()


@api_view(['POST'])
def copy_snapshot_to_new_project(request):
    src_snapshot_id = request.data['srcSnapshotId']
    dst_snapshot_id = request.data['dstSnapshotId']
    dst_project_id = request.data['dstProjectId']
    dst_name = request.data['dstName']

    snapshot = get_object_or_404(Snapshot, id=src_snapshot_id)

    # changing the id makes this ORM object reference a new row in the
    # database
    snapshot.id = dst_snapshot_id
    snapshot.data['snapshotId'] = dst_snapshot_id
    snapshot.data['projectId'] = dst_project_id
    snapshot.data['name'] = dst_name

    snapshot.save()

    return Response()

