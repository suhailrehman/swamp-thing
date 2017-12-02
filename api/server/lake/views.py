from rest_framework import viewsets
from lake.models import Lake, CrawlJob, CrawledItem
from lake.serializers import LakeSerializer
from lake.serializers import CrawlJobSerializer, CrawledItemSerializer
from lake.serializers import CrawledItemListSerializer
from lake.serializers import CrawledItemDetailSerializer
from rest_framework.decorators import detail_route, list_route
import pika
import config.settings as settings
from rest_framework.response import Response
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from lake.utils import get_file_extention_counts
from django.core.exceptions import ObjectDoesNotExist


class LakeViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Lake objects """
    queryset = Lake.objects.all()
    serializer_class = LakeSerializer
    lookup_field = 'name'
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)


class CrawlJobViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing CrawlJob objects """
    queryset = CrawlJob.objects.all()
    serializer_class = CrawlJobSerializer

    @detail_route(methods=['get', 'post'])
    def start(self, request, pk=None):
        # TODO: Validation and Exception Handlers
        crawljob = self.get_object()

        output_data = CrawlJobSerializer(crawljob).data
        connection = pika.BlockingConnection(
            pika.URLParameters(crawljob.lake.aqmp_url))
        channel = connection.channel()
        channel.queue_declare(queue=crawljob.lake.crawl_queue_name)
        channel.basic_publish(exchange='',
                              routing_key=crawljob.lake.crawl_queue_name,
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
        queryset = CrawledItem.objects.all()
        lake = self.request.query_params.get('lake', None)
        directory = self.request.query_params.get('directory', None)
        # todo string representations of True and False in URL
        if lake is not None:
            queryset = queryset.filter(lake__name=lake)
        if directory is not None:
            queryset = queryset.filter(directory=True)
        return queryset

    @list_route(methods=['get'])
    def filetypes(self, request):
        queryset = self.get_queryset()
        top = self.request.query_params.get('top', None)
        return Response({'extensions': get_file_extention_counts(queryset, top)})


class MetaViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for metadata about the system
    """

    def list(self, request):
        num_lakes = Lake.objects.count()
        num_items = CrawledItem.objects.count()
        try:
            last_crawl = CrawlJob.objects.latest(field_name='start_time').start_time.strftime('%Y-%m-%d %H:%M')
        except Exception:
            last_crawl = 'None'
        total_jobs = CrawlJob.objects.count()

        return Response({'num_lakes': num_lakes,
                         'num_items': num_items,
                         'last_crawl': last_crawl,
                         'total_jobs': total_jobs})
