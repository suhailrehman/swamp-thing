# swamp-thing
Filesystem Crawler for the Data Swamp. Conists of the following components

[Front-End API](api/README.md)
is built on Django-Rest-Framework, allows for the specification of a data lake, as well as crawl job specifications (essentially root paths) to start a crawl Job. You can also view the individual objects and list all the discovered files here.

[Crawler](crawler/README.md)
is a java server program that listens on a specific Rabbit Queue (by default, named ``crawl``) for crawl jobs and recurisvely crawls the target, emitting file and directory metadata until the crawl depth specfied in the job is met. Crawled objects are emitted to the 'discover' queue.

[Controller](controller/README.md)
is an additional process that listens to the discover queue and pushes them into the API database. Can be eliminited/integrated into the Crawler code or given more responsibility in the future.


## Requirements
Documentation TODO

This system requires a working RabbitMQ server with appropriate user/permissions configured correctly.

## Installation
Requires each individual component to be installed seperately. Read the respective pages.
