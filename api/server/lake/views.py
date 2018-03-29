from rest_framework import viewsets
from lake.models import *
from lake.serializers import *
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
import json
from rest_framework.parsers import JSONParser



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

    # Custom Serializers so that 4K head does not appear in LIST queries
    # Create has a custom update pathway
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

    #Custom queryset handler to process lake/directory parameters in query
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

    #Return top-k filetypes query
    @list_route(methods=['get'])
    def filetypes(self, request):
        queryset = self.get_queryset()
        top = self.request.query_params.get('top', None)
        return Response({'extensions': get_file_extention_counts(queryset, top)})

    #Return treemap query
    @list_route(methods=['get'])
    def treemap(self, request):
        queryset = self.get_queryset()
        return Response({'treemap': generate_treemap_data(queryset)})


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
        total_keywords = Keyword.objects.count()
        total_topics = Topic.objects.count()
        total_columns = StructuredColumn.objects.count()

        return Response({'num_lakes': num_lakes,
                         'num_items': num_items,
                         'last_crawl': last_crawl,
                         'total_jobs': total_jobs,
                         'total_columns': total_columns,
                         'total_keywords': total_keywords,
                         'total_topics': total_topics})


class StructuredColumnViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing StructuredColumn objects """
    queryset = StructuredColumn.objects.all()
    serializer_class = StructuredColumnSerializer
    lookup_field = 'name'
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'coltype', 'crawled_item')
    ordering_fields = ('minimum', 'maximum', 'average', 'early', 'late')


class TopicViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Keyword objects """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    lookup_field = 'topic_word'
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('topic_word', 'crawled_item__path')
    ordering_fields = ('topic_word')

    #Return wordcloud query
    @list_route(methods=['get'])
    def cloud(self, request):
        queryset = self.get_queryset()
        return Response({'cloud': [[str(q.topic_word), q.crawled_item.all().count()] for q in queryset]})


class KeywordViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Keyword objects """
    queryset = KeywordScore.objects.all()
    serializer_class = KeywordSerializer
    lookup_field = 'keyword'
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('keyword__keyword', 'crawled_item__path')
    ordering_fields = ('keyword__keyword', 'score')


class SklumaViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for metadata about the system
    """

    parser_classes = (JSONParser,)

    def create(self, request):
        errors = []
        num_cols = 0
        num_keywords = 0
        num_topics = 0

        print request.data
        data_object = request.data

        #top-level metadata
        try:
            metadata = data_object['metadata']
            file_path = metadata['file']['path']
        except:
            return Response({'success': 'false', 'error': 'Request does not contain valid metadata and file path objects.'})
        
        #TODO Search for file path in catalog, or create if it doesnt exist
        try:
            crawled_item = CrawledItem.objects.get(path=file_path)
        except:
            return Response({'success': 'false', 'error': 'No crawled files in catalog matching: '+file_path})

        #extractors

        try:
            columns = data_object['extractors']['ex_structured']['cols']

            #For each Column:
            #TODO Handle already existing columns
            for colname, colproperties in columns.iteritems():
                
                print "Adding colname"
                column = {}
                column['name'] = colname
                column['crawled_item'] = crawled_item.id

                #Copy over field properties
                for prop, value in colproperties.iteritems():
                    column[prop] = value

                #Hopefully the column serializes
                serialized_column = StructuredColumnSerializer(data=column)
                if(serialized_column.is_valid()):
                    serialized_column.save()
                    num_cols += 1
                else:
                    #TODO: Failure is an option, don't store column.
                    errors.append({'column': colname, 'column_errors': serialized_column.errors})
                    #return Response({'success': 'false', 'error': 'Could not store column', 'col': column, 'errors': serialized_column.errors})
        except:
            pass

        #topics
        try:
            topics = data_object['extractors']['ex_freetext']['topics']
            for topic in topics:    
                try:
                    existing_topic = Topic.objects.get(topic_word=topic)
                    Topic.crawled_item.add(crawled_item)
                except:
                    # New Topic
                    topic_object = {}
                    topic_object['topic_word'] = topic
                    topic_object['crawled_item'] = [crawled_item.id]
                    serialized_topic = TopicSerializer(data=topic_object)
                    if(serialized_topic.is_valid()):
                        serialized_topic.save()
                        num_topics += 1
                else:
                    #TODO: Failure is an option, don't store column.
                    errors.append({'topic': topic, 'topic_errors': serialized_topic.errors})
                    #return Response({'success': 'false', 'error': 'Could not store topic', 'topic': topic_object, 'errors': serialized_topic.errors})
        except:
            pass
        
        #keywords
        try:
            keywords = data_object['extractors']['ex_freetext']['keywords']
            for keyword, score in keywords.iteritems():
                try:
                    existing_keyword = Keyword.objects.get(keyword=keyword)
                except:
                    existing_keyword = Keyword(keyword=keyword)
                    existing_keyword.save()

                try:
                    kwscore = KeywordScore(keyword=existing_keyword, score=score, crawled_item=crawled_item)
                    kwscore.save()
                    num_keywords += 1
                except Exception as e:
                    #TODO: Failure is an option, don't store column.
                    errors.append({'keyword': keyword, 'keyword_error': e})
                    #return Response({'success': 'false', 'error': 'Could not store keyword', 'keyword': keyword, 'errors': e})
        except:
            pass

        added = {'number of colums': num_cols, 'number of topics': num_topics, 'number of keywords': num_keywords}
        
        if errors:
            return Response({'success': 'partial', 'added': added, 'errors': errors})    
        return Response({'success': 'true', 'added': added})