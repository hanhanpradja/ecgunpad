from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index),
    path("new-pasien-rekam/", views.new_pasien_rekam, name='new_pasien_rekam'),
    path("api/niks/", views.get_registered_niks, name='get_registered_niks'),
    path("process-data/", views.process_data, name='process_data'),
    path("stop-process/", views.stop_process, name='stop_process'),
    path("check-nik/", views.check_nik, name='check_nik'),
    path("test-process-data/", views.test_process_data, name='test_process_data'),
    path('get-process-status/', views.get_process_status, name='get_process_status')
]


