from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.search_page),
    path("search/", views.search, name='search'),
    path("patient-record/", views.patient_record, name='patient_record'),
    path("patient-record/detail/", views.detail),
    path("patient-record/detail/api/sinyalData/", views.get_signal)
]