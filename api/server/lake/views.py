from rest_framework import viewsets
from lake.models import Lake, CrawlJobSpec, CrawlJob, CrawledItem
from lake.serializers import LakeSerializer, CrawlJobSpecSerializer
from lake.serializers import CrawlJobSerializer, CrawledItemSerializer
from rest_framework.decorators import detail_route
import pika
import config.settings as settings
from rest_framework.response import Response
from datetime import datetime
from rest_framework.renderers import JSONRenderer


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

    @detail_route(methods=['get', 'post'])
    def start(self, request, pk=None):
        # TODO: Validation and Exception Handlers
        crawljob = self.get_object()
        jobspec_serializer = CrawlJobSpecSerializer(crawljob.spec)

        output_data = jobspec_serializer.data
        output_data['last_crawl'] = crawljob.uuid
        connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RMQ_SERVER))
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
