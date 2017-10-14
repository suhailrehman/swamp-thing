"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from lake.views import LakeViewSet, CrawlJobSpecViewSet
from lake.views import CrawlJobViewSet, CrawledItemViewSet


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

router = DefaultRouter()
router.register(prefix='lakes', viewset=LakeViewSet)
router.register(prefix='crawljobspecs', viewset=CrawlJobSpecViewSet)
router.register(prefix='crawljobs', viewset=CrawlJobViewSet)
router.register(prefix='crawleditems', viewset=CrawledItemViewSet)

urlpatterns = router.urls
