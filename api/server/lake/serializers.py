from rest_framework import serializers
from lake.models import Lake, CrawlJobSpec, CrawlJob, CrawledItem


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

    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl")