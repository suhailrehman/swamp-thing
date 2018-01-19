# swamp-thing
Filesystem Crawler for the Data Swamp.


## System Design

The crawler is designed with multiple microservices, that communicate with each other using RabbitMQ. The data model used for this system is as follows.

* A data lake consists of multiple filesystems that can be crawled and indexed together. Each data lake requires the creation of a specific RabbitMQ app/password/channel on which multiple queues are managed.

* A data lake can be configured with multiple CrawlJobs, each of which have a specific fully qualified Root URI. All filesystems accessible by the Apache Filesystem API are supported.

* Files and directories discovered during a crawl are CrawledItems, and are currently indexed in the API as such. Each crawleditem, the associated filesystem metadata and 4K head of file are all stored in the Front-End API database.

Consists of the following components:

[Front-End API](api/README.md)
is built on Django-Rest-Framework, allows for the specification of a data lake, as well as crawl job specifications (essentially root paths) to start a crawl Job. You can start crawl jobs and view the individual discovered objects and list all the discovered files here. In addition, a dashboard app provides a neat end-user interface to view and chart all the information discovered during crawling.

[Crawler](crawler/README.md)
is a java server program that listens on a specific Rabbit Queue (by default, named ``crawl``) for crawl jobs and recurisvely crawls the target, emitting file and directory metadata until the crawl depth specfied in the job is met. Crawled objects are emitted to the 'discover' queue.

[Controller](controller/README.md)
is an additional process that listens to the discover queue and pushes them into the API database. Can be eliminited/integrated into the Crawler code or given more responsibility in the future.


## Installation

### Prerequisites
This system requires a working RabbitMQ server with appropriate user/permissions configured correctly for each Data lake that is to be crawled by this system.

Installation Instructions for RabbitMQ and management interface:
```
sudo apt install rabbitmq-server
rabbitmq-plugins enable rabbitmq_management
```

Visit `http://localhost:15672/` and configure a user/password of your choice. The default used in all our configuration files is `app:app`. Thus the default AQMP URL used is `amqp://app:app@server-name:5672/server-name`

Additionally, Python version 2.7 with pip virutalenv is required to deploy the front-end API/dashboard. If not already installed, it can be installed as follows:
```
sudo apt install python-pip
sudo pip install virtualenv
```
The crawler requires a working Maven installation to deploy. The app has been tested with Maven 3.3.9

### Setting up and Installing the Crawler Components

Refer to the individual component installations one-by-one:

[Front-End API](api/README.md)

[Crawler](crawler/README.md)

[Controller](controller/README.md)


## End-to-End Functional Demo Instructions

* Start the RabbitMQ service if it's not running already.
* Start the Front-End API server. Review server/AQMP configuration at [api/server/config/settings.py](api/server/config/settings.py) before starting the server.
  ``` source env/bin/activate
  cd api/server
  ./manage.py runserver 0.0.0.0 8000
  ```
* Configure a data lake and appropriate AQMP URL using the API `http://localhost:8000/api/lakes`
* Configure a crawl job with appropriate root URL and other parameters using `http://localhost:8000/api/crawljobs`
* Run the Crawler Process after setting the appropirate configuration [crawler/src/main/resources/config.properties](crawler/src/main/resources/config.properties)
  ```
  cd crawler
  mvn clean install exec:java
  ```
* Run the controller process after configuring [controller/rmq_listener.py](controller/rmq_listener.py)
  ```
  source env/bin/activate
  cd controller
  ./rmq_listener.py
  ```
* Start the crawljob and view results by visiting the dashboard at `http://localhost:8000/dashboard/`

## Integrating Downstream Analytics

The Datalake API is extensible and more items can be modelled with FQ relationships to CrawledItems. Furthermore, downstream processing can be enabled by listening the the `discover` queue using the same AQMP URL for newly discovered items, as well as an `update` queue which can be used to keep track of items that have been updated since the last crawl.
