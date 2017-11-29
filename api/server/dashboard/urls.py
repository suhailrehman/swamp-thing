from django.conf.urls import url
from dashboard.views import *

urlpatterns = [
    # Homepage
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^lakes$', LakeView.as_view(), name='lakes'),
    url(r'^crawleditems$', CrawledItemsView.as_view(), name='crawleditems'),
]
