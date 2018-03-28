from django.db import models
# from django.core.validators import URLValidator
import config.settings as settings
import uuid
from utils import get_default_aqmp_url


class Lake(models.Model):
    """ Data Lake Model """
    name = models.CharField(primary_key=True, max_length=100, unique=True)
    aqmp_url = models.CharField(max_length=settings.MAX_PATH_LEN, null=False,
                                default=get_default_aqmp_url())
    crawl_queue_name = models.CharField(
        max_length=settings.MAX_PATH_LEN, default='crawl')
    discover_queue_name = models.CharField(
        max_length=settings.MAX_PATH_LEN, default='discover')
    update_queue_name = models.CharField(
        max_length=settings.MAX_PATH_LEN, default='update')

    def __str__(self):
        return self.name


class CrawlJob(models.Model):
    lake = models.ForeignKey(Lake, related_name='jobs',
                             on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField(null=True)

    root_uri = models.CharField(max_length=settings.MAX_PATH_LEN)

    # TODO: URI Validation
    '''root_uri = models.URLField(max_length=settings.MAX_PATH_LEN,
            validators=[URLValidator(schemes=['hdfs', 's3'])])
    '''

    exclusion_patterns = models.CharField(max_length=settings.REGEX_LEN)
    crawl_depth = models.PositiveIntegerField()

    def __str__(self):
        return str(self.uuid) + " (Lake: " + str(self.lake.name) + ")"


class CrawledItem(models.Model):
    lake = models.ForeignKey(Lake, related_name='items',
                             on_delete=models.CASCADE)
    path = models.CharField(max_length=settings.MAX_PATH_LEN)
    directory = models.BooleanField(default=False)
    size = models.PositiveIntegerField(default=0)
    last_modified = models.DateTimeField(null=False)
    owner = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    last_crawl = models.ForeignKey(CrawlJob, related_name='items')
    head_4k = models.CharField(max_length=8192, blank=True, null=True)

    # class Meta:
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

    def __str__(self):
        return str(self.path) + " (Lake: "+str(self.lake.name)+")"


class StructuredColumn(models.Model):
    name = models.CharField(max_length=settings.MAX_PATH_LEN)
    crawled_item = models.ForeignKey(CrawledItem, related_name="columns")

    prec = models.FloatField(null=True)
    minimum = models.FloatField(null=True)
    maximum = models.FloatField(null=True)
    average = models.FloatField(null=True)
    nullval = models.CharField(max_length=settings.MAX_PATH_LEN, null=True)
    early = models.DateTimeField(null=True)
    late = models.DateTimeField(null=True)


    LATSTD = 'lat-std'
    LONSTD = 'lon-std'
    LATEW = 'lat-ew'
    LONEW = 'lon-ew'
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'
    DATETIME = 'datetime'
    NONE = 'none'
    UNKNOWN = 'unknown'
    UUID = 'uuid'

    TYPE_CHOICES = (
        (LATSTD, 'Latitude Standard'),
        (LONSTD,'Longitude Standard'),
        (LATEW, 'Latitude E/W'),
        (LONEW, 'Longitude E/W'),
        (INT, 'Integer'),
        (FLOAT, 'Floating Point'),
        (STRING, 'String'),
        (DATETIME, 'Date / Time'),
        (NONE, 'None'),
        (UNKNOWN, 'Unknown Column'),
        (UUID, 'uuid')
        )

    coltype = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=NONE,
    )
    
    class Meta:
        unique_together = ('name', 'crawled_item')


class Topic(models.Model):
    topic_word = models.CharField(max_length=settings.MAX_PATH_LEN, unique=True)
    crawled_item = models.ManyToManyField(CrawledItem, related_name="topics")


class Keyword(models.Model):
    keyword = models.CharField(max_length=settings.MAX_PATH_LEN, unique=True)
    
    def __str__(self):
        return str(self.keyword)


class KeywordScore(models.Model):
    keyword = models.ForeignKey(Keyword, related_name="scores") 
    score = models.FloatField(null=True)
    crawled_item = models.ForeignKey(CrawledItem, related_name="keywordscores")

    class Meta:
        unique_together = ('keyword', 'crawled_item')