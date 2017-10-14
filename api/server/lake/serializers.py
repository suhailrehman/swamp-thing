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
            "uuid", "spec", "running", "start_time"
        )
        read_only_fields = ('start_time', 'running')


class CrawledItemSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Employee model """
    class Meta:
        model = CrawledItem
        fields = ("id", "lake", "path", "directory", "size",
                  "last_modified", "owner", "last_crawl")
