"""luckyapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from .api_routers import no_slash_router, router

# Django 3.2+ の admin は未定義パスをログイン画面へ転送するため、
# 従来の /admin/attendee/ が router に届くよう無効にします
admin.site.final_catch_all_view = False

API_V1_BASE_PATH = "api/v1/"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/", include(router.urls)),
    path(API_V1_BASE_PATH, include(router.urls)),  # include api url pattern here
    path("admin/", include(no_slash_router.urls)),
    path(API_V1_BASE_PATH, include(no_slash_router.urls)),
]
