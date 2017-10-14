from django.db import models
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
    root_uri = models.URLField(max_length=settings.MAX_PATH_LEN)
    exclusion_patterns = models.CharField(max_length=settings.REGEX_LEN)
    crawl_depth = models.PositiveIntegerField()

    def __str__(self):
        return self.uuid + " (Lake: " + str(self.lake.name) + ")"


class CrawlJob(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4, editable=False)
    lake = models.ForeignKey(Lake, related_name='jobs')
    spec = models.ForeignKey(CrawlJobSpec)
    start_time = models.DateTimeField(auto_now_add=True)
    running = models.BooleanField(default=False)


class CrawledItem(models.Model):
    lake = models.ForeignKey(Lake, related_name='items')
    path = models.URLField(max_length=settings.MAX_PATH_LEN)
    directory = models.BooleanField(default=False)
    size = models.PositiveIntegerField(default=0)
    last_modified = models.DateTimeField(null=False)
    owner = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    last_crawl = models.ForeignKey(CrawlJob, related_name='items')

    '''
    HDFS = 'HD'
    S3 = 'S3'
    FS_TYPE = (
        (HDFS, 'HDFS'),
        (S3, 'S3')
    )
    '''
