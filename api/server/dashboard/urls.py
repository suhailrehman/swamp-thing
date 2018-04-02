from django.conf.urls import url
from dashboard.views import *

urlpatterns = [
    # Homepage
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^lakes$', LakeView.as_view(), name='lakes'),
    url(r'^crawleditems$', CrawledItemsView.as_view(), name='crawleditems'),
    url(r'^keywords$', KeywordsView.as_view(), name='keywords'),
    url(r'^columns$', ColumnsView.as_view(), name='columns'),
    url(r'^topics$', TopicsView.as_view(), name='topics'),
]
