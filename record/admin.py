from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.RekamanEKG)
admin.site.register(models.IntervalData)
admin.site.register(models.SinyalData)