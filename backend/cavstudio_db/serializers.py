from cavstudio_db.models import SearchSet, Snapshot
from rest_framework import serializers


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = ['id', 'data']


class SearchSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSet
        fields = ['id', 'data']
