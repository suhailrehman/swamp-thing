from django.db import models
from django.core.validators import URLValidator
import config.settings as settings
import uuid


class Lake(models.Model):
    """ Data Lake Model """
    name = models.CharField(primary_key=True, max_length=100, unique=True)

    def __str__(self):
        return self.name


class CrawlJobSpec(models.Model):
    """ Start of a Crawl Path """
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4, editable=False)
    lake = models.ForeignKey(Lake, related_name='specs')
    root_uri = models.CharField(max_length=settings.MAX_PATH_LEN)
    # TODO: URI Validation
    '''root_uri = models.URLField(max_length=settings.MAX_PATH_LEN,
                               validators=[URLValidator(schemes=['hdfs', 's3'])])
    '''
    exclusion_patterns = models.CharField(max_length=settings.REGEX_LEN)
    crawl_depth = models.PositiveIntegerField()

    def __str__(self):
        return str(self.uuid) + " (Lake: " + str(self.lake.name) + ")"


class CrawlJob(models.Model):
    lake = models.ForeignKey(Lake, related_name='jobs')
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4, editable=False)
    spec = models.ForeignKey(CrawlJobSpec)
    start_time = models.DateTimeField(null=True)
    running = models.BooleanField(default=False)


class CrawledItem(models.Model):
    lake = models.ForeignKey(Lake, related_name='items')
    path = models.CharField(max_length=settings.MAX_PATH_LEN)
    directory = models.BooleanField(default=False)
    size = models.PositiveIntegerField(default=0)
    last_modified = models.DateTimeField(null=False)
    owner = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    last_crawl = models.ForeignKey(CrawlJob, related_name='items')
    head_4k = models.CharField(max_length=8192, null=True)

    #class Meta:
    #    unique_together = ('lake', 'path')

    def compare_versions(self, validated_data):
        new_timestamp = validated_data.get('last_modified')
        old_timestamp = self.last_modified
        if new_timestamp > old_timestamp:
            return 1
        elif new_timestamp == old_timestamp:
            return 0
        else:
            return -1
    '''
    HDFS = 'HD'
    S3 = 'S3'
    FS_TYPE = (
        (HDFS, 'HDFS'),
        (S3, 'S3')
    )
    '''
