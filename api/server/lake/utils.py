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


# TODO: Cleanup or move method to better location
# Recursive function to parse pathname and construct a nested treemap dict
def attach(path_name, root, size, dir):
    '''
    Insert a path_name of directories on its root.
    '''
    parts = path_name.split('/', 1)
    if len(parts) == 1:  # path_name is a file
        if not dir:
            root.append({"key": parts[0], "value": size})
    else:
        node, others = parts
        if node not in [item['key'] for item in root]:
            new_node = {"key": node, "values": []}
            root.append(new_node)
            attach(others, new_node['values'], size, dir)
        else:
            for item in root:
                if item['key'] == node:
                    try:
                        attach(others, item['values'], size, dir)
                    except Exception:
                        pass


def generate_treemap_data(queryset):

    return_list = []

    '''
    Treemap reference: http://bl.ocks.org/ganeshv/6a8e9ada3ab7f2d88022
    Sample Data to be generated:

    [
      {
        "key": "Asia",
        "values": [
        {
          "key": "India",
          "value": 1236670000
        },
        {
          "key": "China",
          "value": 1361170000
        },
        ...
      },
      {
        "key": "Africa",
        "values": [
        {
          "key": "Nigeria",
          "value": 173615000
        },
        {
          "key": "Egypt",
          "value": 83661000
        },
        ...
      },
    ]
    '''
    for item in queryset:
        attach(item.path, return_list, item.size, item.directory)

    return return_list