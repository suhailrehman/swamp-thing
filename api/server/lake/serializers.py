from rest_framework import serializers
from lake.models import Lake, CrawlJob, CrawledItem
import pika
import config.settings as settings
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist


class LakeSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Chain model """
    class Meta:
        model = Lake
        fields = ["name"]


class CrawlJobSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Store model """
    class Meta:
        model = CrawlJob
        fields = (
            "lake", "uuid", "running", "start_time", "root_uri",
            "exclusion_patterns", "crawl_depth"
        )
        read_only_fields = ('start_time', 'running')


class CrawledItemSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Employee model """

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
                    pika.URLParameters(settings.AQMP_URL))
                channel = connection.channel()
                channel.queue_declare(queue='updates')
                channel.basic_publish(exchange='',
                                      routing_key='updates',
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
        fields = ("id", "lake", "path", "directory", "size", "owner", "last_modified")


class CrawledItemDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl", "head_4k")