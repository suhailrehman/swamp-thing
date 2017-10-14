from rest_framework import viewsets
from lake.models import Lake, CrawlJobSpec, CrawlJob, CrawledItem
from lake.serializers import LakeSerializer, CrawlJobSpecSerializer
from lake.serializers import CrawlJobSerializer, CrawledItemSerializer


class LakeViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Lake objects """
    queryset = Lake.objects.all()
    serializer_class = LakeSerializer
    lookup_field = 'name'


class CrawlJobSpecViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawlJobSpec objects """
    queryset = CrawlJobSpec.objects.all()
    serializer_class = CrawlJobSpecSerializer


class CrawlJobViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawlJob objects """
    queryset = CrawlJob.objects.all()
    serializer_class = CrawlJobSerializer


class CrawledItemViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawledItem objects """
    queryset = CrawledItem.objects.all()
    serializer_class = CrawledItemSerializer
