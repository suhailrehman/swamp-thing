# swamp-thing Crawler

## Task List
- [X] Clean & Refactor Crawler for Single point crawling
- [X] Add Rabbit API
- [ ] Document
- [ ] Command-line runtime/packaged configuration

# Requirements
Working Maven build system

# Instructions

Configure the RabbitMQ parameters in [src/main/resources/config.properties](src/main/resources/config.properties).

# Building and Running
The following command will build, run tests and execute the crawler:

```
 mvn clean install exec:java
```

# HDFS Crawling
URI in the job specification must have complete HDFS path URI including the hostname as described in the Hadoop environemnt using the parameter `fs.default.name`. An easy way to find out what it is for your file system is the following command:

```
hdfs getconf -confKey fs.default.name
```

A working jobspec for the NUC hdfs:

```
{
        "uuid": "d0f720f8-1704-4848-98ba-117a2a9c2954",
        "lake": "HDFSLakeNUC",
        "root_uri": "hdfs://madison-master:9000/",
        "exclusion_patterns": "(.*)(/\\\\.)(.*)",
        "crawl_depth": 10
}
```

Extraction of the 4k head of file requires DFS permissions of the user running this crawl process, process will log warnings in case if it unable to access files because of IO or permissions problems, but will continue to crawl.


