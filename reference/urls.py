from django.urls import path, include

from . import views
import dashboard

urlpatterns = [
    path("", views.index),
    path('stop-process/', dashboard.views.stop_process)
]