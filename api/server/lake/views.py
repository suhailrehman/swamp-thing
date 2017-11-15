from rest_framework import viewsets
from lake.models import Lake, CrawlJobSpec, CrawlJob, CrawledItem
from lake.serializers import LakeSerializer, CrawlJobSpecSerializer
from lake.serializers import CrawlJobSerializer, CrawledItemSerializer
from lake.serializers import CrawledItemListSerializer
from lake.serializers import CrawledItemDetailSerializer
from rest_framework.decorators import detail_route
import pika
import config.settings as settings
from rest_framework.response import Response
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class LakeViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Lake objects """
    queryset = Lake.objects.all()
    serializer_class = LakeSerializer
    lookup_field = 'name'
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)


class CrawlJobSpecViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawlJobSpec objects """
    queryset = CrawlJobSpec.objects.all()
    serializer_class = CrawlJobSpecSerializer


class CrawlJobViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawlJob objects """
    queryset = CrawlJob.objects.all()
    serializer_class = CrawlJobSerializer

    @detail_route(methods=['get', 'post'])
    def start(self, request, pk=None):
        # TODO: Validation and Exception Handlers
        crawljob = self.get_object()
        jobspec_serializer = CrawlJobSpecSerializer(crawljob.spec)

        output_data = jobspec_serializer.data
        output_data['last_crawl'] = crawljob.uuid
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.AQMP_URL))
        channel = connection.channel()
        channel.queue_declare(queue='crawl')
        channel.basic_publish(exchange='',
                              routing_key='crawl',
                              body=JSONRenderer().render(output_data))
        crawljob.running = True
        crawljob.start_time = datetime.now()
        crawljob.save()
        return Response({'status': 'started', 'sent_data': output_data})

    @detail_route(methods=['post'])
    def stop(self, request, pk=None):
        crawljob = self.get_object()
        crawljob.running = False
        # TODO: Actually Pruge Queue of pending messages and
        # send message to crawler to stop crawl for specific UUID
        crawljob.save()


class CrawledItemViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawledItem objects """
    queryset = CrawledItem.objects.all()
    serializer_class = CrawledItemSerializer

    action_serializers = {
        'retrieve': CrawledItemDetailSerializer,
        'list': CrawledItemListSerializer,
        'create': CrawledItemSerializer
    }

    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('path', 'lake__name', 'owner', 'group')
    ordering_fields = ('size', 'last_modified')

    def get_serializer_class(self):

        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super(CrawledItemViewSet, self).get_serializer_class()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = CrawledItem.objects.all()
        lake = self.request.query_params.get('lake', None)
        if lake is not None:
            queryset = queryset.filter(lake__name=lake)
        return queryset
