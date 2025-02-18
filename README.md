# Train Station

A simplified train, station, travel and crew management system. Built on Django Rest Framework

## Installing using GitHub

Install PostgreSQL and create db

```shell
git clone <link>
cd train_station
python -m venv venv
source venv\Scripts\activate
pip install requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db User password>
set DJANGO_SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver
```

## Getting started with Docker

Build containers in docker-compose file with command,
docker should be installed

```shell
docker-compose build
```

And start it with command

```shell
docker-compose up
```

## Getting access
Open your browser and enter the domain

```shell
http://127.0.0.1:8001/api/station/
```

You can create your user own User here

```shell
http://127.0.0.1:8001/api/user/create/
```

Or you can use already created users:
Regular user:
    username: sampleuser@test.com
    password: samplepassword3223
Admin or Superuser:
    username: sampleadmin@test.com
    password: heater2332

You can get access token here

```shell
http://127.0.0.1:8001/api/user/token/
```

## Features

* JWT authenticated
* Admin panel
* Managing orders and tickets
* Creating trains, journeys, routs...
* Filtering journey by route id and date

To get acquainted with all endpoints you can read
swagger documentation by link

```shell
http://127.0.0.1:8001/api/doc/swagger/#/station
```