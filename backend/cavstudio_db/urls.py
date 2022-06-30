# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.urls import path

from . import views

urlpatterns = [
    path('get_all_snapshots_for_project_including_snapshot', views.get_all_snapshots_for_project_including_snapshot),
    path('get_user_projects_summary', views.get_user_projects_summary),
    path('get_snapshot', views.get_snapshot),
    path('set_snapshot', views.set_snapshot),
    path('delete_snapshot', views.delete_snapshot),
    path('get_search_sets', views.get_search_sets),
    path('get_search_set', views.get_search_set),
    path('set_search_set', views.set_search_set),
    path('delete_search_set', views.delete_search_set),
    path('copy_snapshot_to_new_project', views.copy_snapshot_to_new_project),
]
