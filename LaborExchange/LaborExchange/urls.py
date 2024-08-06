"""LaborExchange URL Configuration
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""


from django.contrib import admin
from django.urls import path, include

from PersonalArea.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("PersonalArea.urls")),
]

handler404 = pageNotFound
