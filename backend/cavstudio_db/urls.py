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
