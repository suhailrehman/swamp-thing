from lake.models import CrawledItem
import os
from collections import Counter


def get_file_extention_counts(queryset, top):
    path_list = queryset.values_list('path', flat=True)
    try:
        topint = int(top)
    except Exception:
        topint = None
    return Counter([os.path.splitext(path)[1] for path in path_list]).most_common(topint)
