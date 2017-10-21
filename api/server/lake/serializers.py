from rest_framework import serializers
from lake.models import Lake, CrawlJobSpec, CrawlJob, CrawledItem
import pika
import config.settings as settings
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist


class LakeSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Chain model """
    class Meta:
        model = Lake
        fields = ["name"]


class CrawlJobSpecSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Store model """
    class Meta:
        model = CrawlJobSpec
        fields = ("uuid", "lake", "root_uri",
                  "exclusion_patterns", "crawl_depth")


class CrawlJobSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Store model """
    class Meta:
        model = CrawlJob
        fields = (
            "lake", "uuid", "spec", "running", "start_time"
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
            existing_item = CrawledItem.objects.get(
                lake=validated_data.get('lake', None),
                path=validated_data.get('path', None))
            if existing_item.compare_versions(existing_item, validated_data) > 1:
                # Send this item on the update queue
                existing_item.update(**validated_data)
                item_serializer = CrawledItemSerializer(existing_item)
                connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RMQ_SERVER))
                channel = connection.channel()
                channel.queue_declare(queue='updates')
                channel.basic_publish(exchange='',
                                      routing_key='updates',
                                      body=JSONRenderer().render(item_serializer.data))
                pass
            # TODO: Handle case of timestamp rolling back, return an error via API
        except ObjectDoesNotExist:
            CrawledItem.objects.create(**validated_data)

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl")
