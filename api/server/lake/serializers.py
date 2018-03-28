from rest_framework import serializers
from lake.models import *
import pika
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist
from utils import *


class LakeSerializer(serializers.ModelSerializer):
    """ Serializer to represent a Lake """
    aqmp_url = serializers.CharField(initial=get_default_aqmp_url())
    crawl_queue_name = serializers.CharField(initial="crawl")
    discover_queue_name = serializers.CharField(initial="discover")
    update_queue_name = serializers.CharField(initial="updates")

    class Meta:
        model = Lake
        fields = ["name", "aqmp_url",
                  "crawl_queue_name",
                  "discover_queue_name",
                  "update_queue_name"]


class CrawlJobSerializer(serializers.ModelSerializer):
    """ Serializer to represent a CrawlJob """
    class Meta:
        model = CrawlJob
        fields = (
            "lake", "uuid", "start_time", "root_uri",
            "exclusion_patterns", "crawl_depth"
        )
        read_only_fields = ('start_time', 'running')


class CrawledItemSerializer(serializers.ModelSerializer):
    """ Serializer to represent the CraweledItem """

    """
    Example: '{"crawl_job_uuid":"10a3a312-fc4b-4e87-b81a-f9cce65fb321",
    "path":"file:/home/suhail/Downloads/sample.jpg",
    "file_size":673,"directory":false,"owner_name":"suhail",
    "group_name":"suhail","modification_time":1476461630000}'
    """

    def create(self, validated_data):
        try:
            # print "Item Match!"
            existing_item = CrawledItem.objects.get(
                lake=validated_data.get('lake', None),
                path=validated_data.get('path', None))
            for attr, value in validated_data.items():
                setattr(existing_item, attr, value)
            existing_item.save()
            if existing_item.compare_versions(validated_data) > 1:
                # Send this item on the update queue
                item_serializer = CrawledItemSerializer(existing_item)
                connection = pika.BlockingConnection(
                    pika.URLParameters(existing_item.lake.aqmp_url))
                channel = connection.channel()
                channel.queue_declare(
                    queue=existing_item.lake.update_queue_name)
                channel.basic_publish(exchange='',
                                      routing_key=existing_item.lake.update_queue_name,
                                      body=JSONRenderer().render(item_serializer.data))
            # TODO: Handle case of timestamp rolling back, return an error via API
            return existing_item
        except ObjectDoesNotExist:
            print "Creating Item"
            return CrawledItem.objects.create(**validated_data)

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl", "head_4k")


class CrawledItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory",
                  "size", "owner", "last_modified")


class CrawledItemDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl", "head_4k")


class StructuredColumnSerializer(serializers.ModelSerializer):
    """ Serializer to represent a Structured Column"""
   
    #type = serializers.ChoiceField(source="type", choices=StructuredColumn.TYPE_CHOICES)
    #minimum = serializers.FloatField(source='min', required=False)
    #maximum = serializers.FloatField(source='max', required=False)
    #nullval = serializers.CharField(source='null', required=False)
    #average = serializers.FloatField(source='avg', required=False)
    path = serializers.StringRelatedField(required=False, source="crawled_item")

    class Meta:
        model = StructuredColumn
        fields = (
            "name", "crawled_item", "type",
            "prec","min","max","avg","null","early","late","path")

 #Custom field mappings since we can't use min/max/type in python as they are reserved keywords
StructuredColumnSerializer._declared_fields["type"] = serializers.CharField(source="coltype")
StructuredColumnSerializer._declared_fields["min"] = serializers.FloatField(source="minimum", required=False)
StructuredColumnSerializer._declared_fields["max"] = serializers.FloatField(source="maximum", required=False)
StructuredColumnSerializer._declared_fields["null"] = serializers.CharField(source="nullval", required=False)
StructuredColumnSerializer._declared_fields["avg"] = serializers.FloatField(source="average", required=False)


class TopicSerializer(serializers.ModelSerializer):
    """ Serializer to represent a Topic"""
    path = serializers.SlugRelatedField(read_only=True, slug_field="path", many=True, source="crawled_item")
    class Meta:
        model = Topic
        fields = (
            "topic_word", "crawled_item", "path")


class KeywordSerializer(serializers.ModelSerializer):
    """ Serializer to represent a Keyword"""
    keyword = serializers.StringRelatedField()
    path = serializers.StringRelatedField(required=False, source="crawled_item")

    class Meta:
        model = KeywordScore
        fields = ("keyword", "score", "crawled_item", "path")