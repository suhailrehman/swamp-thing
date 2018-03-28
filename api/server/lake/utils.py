import os, json
from collections import Counter
from config import settings

#from lake.models import CrawledItem
#from lake.serializers import StructuredColumnSerializer, TopicSerializer, KeywordSerializer


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


'''
def skluma_serializer():

    #debug 
    json_data = open('/home/suhail/Scratch/sample.json').read()
    data = json.loads(json_data)

    #top-level metadata
    metadata = data['metadata']
    file_path = metadata['file']['path']
    #TODO Search for file path in catalog, or create if it doesnt exist
    crawled_item = CrawledItem.objects.get(path=file_path)


    #extractors
    columns = data['extractors']['ex_structured']['cols']

    #For each Column:
    #TODO Handle already existing columns
    for colname, colproperties in columns.iteritems():
        
        column = {}
        column['name'] = colname
        column['crawled_item'] = crawled_item.path

        #Copy over field properties
        for prop, value in colproperties.iteritems():
            column[prop] = value

        #Hopefully the column serializes
        serialized_column = StructuredColumnSerializer(data=column)
        if(serialized_column.is_valid()):
            serialized_column.save()


'''
'''
    #topics
    topics = data['extractors']['ex_freetext']['topics']
    for topic in topics:
        topic_object = {}
        topic_object['topic_word'] = topic
        topic_object['crawled_item'] = crawled_item.path

        serialized_topic = TopicSerializer(data=topic_object)
        if(serialized_topic.is_valid()):
            serialized_topic.save()


    #keywords
    keywords = data['extractors']['ex_freetext']['keywords']
    for keyword, score in keywords:
        keyword_object = {}
        keyword_object['keyword'] = keyword
        keyword_object['score'] = score

        serialized_keyword = KeywordSerializer(data=keyword_object)
        if(serialized_keyword.is_valid()):
            serialized_keyword.save()
'''



