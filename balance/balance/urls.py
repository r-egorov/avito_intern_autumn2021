"""balance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path

from .api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/change-balance/", views.ChangeBalance.as_view(), name="change-balance"),
    re_path(r"^api/get-balance/(?P<user_id>\d+)/(?:currency=(?P<currency>\w+)/)?$",
            views.GetBalance.as_view(), name="get-balance"),
    path("api/make-transfer/", views.MakeTransfer.as_view(), name="make-transfer"),
    re_path(r"^api/get-transactions/(?P<user_id>\d+)/(?:sort_by=(?P<sort_by>\w+)/)?$",
            views.GetTransactions.as_view(), name="get-transactions")
]
