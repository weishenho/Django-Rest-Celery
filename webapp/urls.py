"""Technical_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^api/(?P<app_label>\w+)/(?P<model_name>\w+)$', views.GeneralViewSet.as_view({'get': 'list', 'post':'create'})),
    re_path(r'^api/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>[0-9]+)$', views.GeneralViewSet2.as_view({'get': 'retrieve', 'put':'update', 'delete':'destroy'})),
    re_path(r'^fileupload$', views.model_upload)
]

views.one_time_setup()