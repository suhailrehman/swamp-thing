# swamp-thing Controller

## Task List
- [X] Basic Controller
- [ ] Controller Design
- [ ] DB hooks
- [ ] Documentation

# Purpose
An extra hook that monitors the discovery queue and puts discovered items into the API `crawleditems` database

# Configuration
Configure the RabbitMQ server URL in [rmq_lisenter.py](rmq_lisenter.py]) in the variable `AQMP_URL`
