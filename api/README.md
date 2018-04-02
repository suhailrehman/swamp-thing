# swamp-thing API

## Task List
- [x] Initial DRF Project
- [x] Initial Model Design
- [x] Working API tree
- [x] Queue Interaction
- [ ] Crawl Job end detection / queue flushing
- [X] Documentation
- [ ] Unit Tests
- [ ] Production deployment and security settings
- [X] Lake specific Rabbit Queues


# Requirements
Requires virtualenv, python. The API is built using the Django REST Framework (included in the python requirements.txt). Data is written to SQLite during development.

# Installation
```
# Set up a python virtual environment
cd api
virtualenv env

# Activate the environment
source env/bin/activate

# Install required python packages
pip install -r requirements.txt

# Setup the backing database store
./manage.py makemigrations lake
./manage.py migrate

# Run API server
./manage.py runserver
```


# RabbitMQ Configuration
Configure the RabbitMQ server URL in [server/config/settings.py](server/config/settings.py) in the variable `AQMP_URL`

# Access the API server
Once the server is running, it is accessible at http://localhost:8000/