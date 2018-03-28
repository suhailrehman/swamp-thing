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
# from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from lake.views import *

# Lake API Router

app_name = 'api'

router = DefaultRouter()
router.register(prefix='lakes', viewset=LakeViewSet)
router.register(prefix='crawljobs', viewset=CrawlJobViewSet)
router.register(prefix='crawleditems', viewset=CrawledItemViewSet)
router.register(prefix='structuredcolumns', viewset=StructuredColumnViewSet)
router.register(prefix='topics', viewset=TopicViewSet)
router.register(prefix='keywords', viewset=KeywordViewSet)
router.register(prefix='meta', base_name='meta', viewset=MetaViewSet)
router.register(prefix='skluma', base_name='skluma', viewset=SklumaViewSet)

urlpatterns = []
urlpatterns += router.urls
