import os
from collections import Counter
from config import settings


def get_file_extention_counts(queryset, top):
    path_list = queryset.values_list('path', flat=True)
    try:
        topint = int(top)
    except Exception:
        topint = None
    toplist = [os.path.splitext(path)[1] for path in path_list]
    return Counter(toplist).most_common(topint)


def get_default_aqmp_url():
    sitename = settings.CURRENT_HOSTNAME
    return 'amqp://app:app@' + sitename + ':5672/' + sitename
