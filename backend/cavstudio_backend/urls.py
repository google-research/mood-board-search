from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from cavstudio_backend import views

urlpatterns = [
    path('api/ping_cav_server', views.ping),
    path('api/upload_image', views.upload_image),
    path('api/generate_cav', views.generate_cav),
    path('api/inspect', views.inspect),
    path('api/crops', views.crops),
    path('api/heatmap', views.heatmap),
    path('api/image_set/<str:name>', views.image_set),

    path('api/db/', include('cavstudio_db.urls')),

    # retained for backward compatibility
    path('api/scout_images/<str:name>', views.image_set),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.STATIC_CAV_CONTENT_URL, document_root=settings.STATIC_CAV_CONTENT_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
