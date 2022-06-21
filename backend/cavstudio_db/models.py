from django.db import models

# note (joerick):
# this app was originally written against a nosql database (firebase), so we
# are reimplementing that data structure here. It's far from idiomatic Django,
# but it works fine on a local SQLite database.


class Snapshot(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    data = models.JSONField()


class SearchSet(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    data = models.JSONField()
